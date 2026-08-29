from __future__ import annotations

import threading
import time
from collections import deque

from strands.hooks import AfterModelCallEvent, BeforeModelCallEvent, HookProvider, HookRegistry

WINDOW_SECONDS = 60.0
CHARS_PER_TOKEN = 3.6


class TokenBudget:
    def __init__(self, tokens_per_minute: int, headroom: float = 0.8) -> None:
        self.budget = int(tokens_per_minute * headroom)
        self._spent: deque[tuple[float, int]] = deque()
        self._lock = threading.Lock()

    def _prune(self, now: float) -> None:
        while self._spent and now - self._spent[0][0] > WINDOW_SECONDS:
            self._spent.popleft()

    def _in_window(self, now: float) -> int:
        self._prune(now)
        return sum(tokens for _, tokens in self._spent)

    def wait_for(self, tokens: int) -> float:
        waited = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                if self._in_window(now) + tokens <= self.budget or not self._spent:
                    self._spent.append((now, tokens))
                    return waited
                oldest = self._spent[0][0]
            pause = max(0.5, WINDOW_SECONDS - (time.monotonic() - oldest) + 0.5)
            time.sleep(pause)
            waited += pause

    def record_actual(self, estimated: int, actual: int) -> None:
        with self._lock:
            if self._spent:
                stamp, _ = self._spent[-1]
                self._spent[-1] = (stamp, max(actual, estimated))


class PaceModelCalls(HookProvider):
    def __init__(self, budget: TokenBudget, reserve_for_output: int) -> None:
        self.budget = budget
        self.reserve_for_output = reserve_for_output
        self.total_waited = 0.0
        self.calls = 0

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeModelCallEvent, self._before)
        registry.add_callback(AfterModelCallEvent, self._after)

    def _estimate(self, event: BeforeModelCallEvent) -> int:
        text = str(getattr(event.agent, "messages", ""))
        return int(len(text) / CHARS_PER_TOKEN) + self.reserve_for_output

    def _before(self, event: BeforeModelCallEvent) -> None:
        self.calls += 1
        self._last_estimate = self._estimate(event)
        self.total_waited += self.budget.wait_for(self._last_estimate)

    def _after(self, event: AfterModelCallEvent) -> None:
        usage = getattr(getattr(event, "usage", None), "total_tokens", None)
        if usage:
            self.budget.record_actual(getattr(self, "_last_estimate", 0), int(usage))


_shared_budget: TokenBudget | None = None


def shared_budget() -> TokenBudget:
    global _shared_budget
    if _shared_budget is None:
        from app.core.config import get_settings

        limit = 70000 if get_settings().model_provider == "bedrock" else 8000
        _shared_budget = TokenBudget(tokens_per_minute=limit)
    return _shared_budget


def pacer(reserve_for_output: int = 1100) -> PaceModelCalls:
    return PaceModelCalls(shared_budget(), reserve_for_output)
