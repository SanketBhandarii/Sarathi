# Sarathi

**An agent that watches every government exam in India for one student, and stays silent until something actually needs them.**

Built with the [Strands Agents SDK](https://strandsagents.com) for the AWS **Agents for Humans** hackathon, Everyday Agents track.

---

## The problem

A student sits one exam a year. They fight paperwork all year.

Three things go wrong, and they stack:

1. **They do not know what exists.** Thirty lakh people fight for SSC CGL. Meanwhile RBI Grade B, NABARD and SEBI take far fewer applicants, because far fewer people have heard of them.
2. **They do not know if they qualify.** Eligibility is five rules multiplied together: age, category relaxation, qualification level, domicile, attempts used. Most find out only after paying the fee.
3. **Then the paperwork takes it away.** The photo must be 20 to 50 KB. From 2026 SSC will not accept a gallery photo at all. The correction window opens for five days and nobody announces it.

A missed form costs a year of a life.

## What Sarathi does

It reads the commission's own notification, works out whether **this** student can apply, and shows the sentence it based that on. Then it holds every date and makes every file the form demands.

Most nights it runs hundreds of checks and writes to the student about none of them. **Silence is the feature.**

---

## The rule the whole thing rests on

> Every fact Sarathi states must trace to a clause in an official notification PDF. If it cannot find the line, it does not state the fact.

Every verdict on screen carries a page number and the exact sentence:

```
You get 3 extra years because you are OBC.
   page 6: "2 Other Backward Classes (Non-Creamy Layer) 3 years"

Your age is fine. You are 21 and the limit for you is 33.
   page 6: "II. AGE (AS ON 01.07.2026) Minimum: 20 years Maximum: 30 years"
```

A judge who knows nothing about Indian exams can verify the whole system in thirty seconds: open the PDF, go to page 6, read the line.

---

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full diagram.

```
official sites ──► cache PDFs ──► classify ──► READER ⇄ CHECKER ──► verify in code
 ssc upsc ibps      by hash       is this a    (Strands cyclic       quote on page?
 mpsc (browser)    + origin       real          Graph, loops back    number in quote?
                                  notification? on a bad reading)           │
                                                                            ▼
  student profile ──────────────────────────────────────────────►  verdict engine
  age, category, domicile,                                         (plain Python,
  education ladder                                                  no model)
                                                                            │
                                    ┌───────────────────────────────────────┤
                                    ▼                                       ▼
                              Exam Radar                            nightly journal
                        4 layers, 6 buckets                      hundreds of checks,
                         every reason cited                       usually 0 messages
```

### How Strands is used

| Piece | Where |
|---|---|
| `Agent` | reader, checker, extractor, verifier, classifier, spec reader |
| `@tool` | `read_section`, `record_age_rule`, `check_what_was_recorded`, `quote_appears_on_page`, `find_text_in_document` |
| `GraphBuilder` | a **cyclic** graph: reader → checker, and an edge back to the reader that only fires when problems were reported |
| `reset_on_revisit` | so a corrected reading starts clean |
| `EdgeCondition` | the loop-back only fires on "problems found" |
| `structured_output` | rules extracted straight into typed Pydantic schemas |
| `ModelRetryStrategy` | native retry on rate limits |
| Hooks (`BeforeModelCallEvent`) | a token-budget pacer that respects the provider's per-minute limit |
| `BedrockModel` / `LiteLLMModel` | one env var switches provider; the code never knows |

### The part that matters most

**No model decides who is eligible.** The agents read the document. The arithmetic is plain Python.

Verification runs in three layers, and two of them use no AI at all:

1. Is the quoted sentence actually on the page it cites? *(string matching)*
2. Does the recorded number actually appear in that sentence? *(arithmetic)*
3. Anything the first two cannot see *(an agent with tools)*

Layers 1 and 2 exist because of something found during development: planted errors — max age 30 changed to 45, OBC relaxation 3 changed to 9 — were **missed by the AI verifier and caught instantly by the plain checks.** The most dangerous error in this product is a real quote paired with a wrong number, and a model can be fooled by it. Arithmetic cannot.

---

## What it does, feature by feature

| | |
|---|---|
| **Exam Radar** | Every exam in four layers: Central, your State, your City, other states open to all. Nothing is hidden; exams you cannot take are shown with the reason. |
| **Verdict engine** | Age with category relaxation, qualification **level**, marks, fees, domicile. Six buckets including "closed for now, it runs again" — because telling a student CGL is "not for you" would be a lie. |
| **Education ladder** | 10th, 12th, ITI, Diploma, Graduation, PG. Percentage or CGPA with live conversion. A diploma does not satisfy a degree requirement, and desirable qualifications never block. |
| **Document maker** | Reads the size rules out of the notification, then turns a phone photo into the exact pixels and byte range. Per commission, because SSC wants a 236×79 signature and IBPS wants 140×60. |
| **Agent Journal** | Every nightly run recorded: sources checked, quotes re-verified, rules evaluated, messages sent. Usually zero. |
| **When I was wrong** | Compares two readings of a notification and says plainly what changed, with the clause from each. A date that moves *earlier* is flagged differently, because only that one costs a student time. |
| **Deadlines + age cliff** | "You turn 34 on 14 November 2028. That day one exam closes to you permanently." |
| **Fee savings** | An SC candidate pays ₹175 where others pay ₹850. Most never realise. |
| **Two languages** | English and Hindi, with a test that fails if either is missing. |

---

## Running it

### You need

- Python 3.11+ and Node 20+
- A Postgres database ([Neon](https://neon.tech) free tier works)
- A model provider: [Groq](https://console.groq.com) (free) **or** AWS Bedrock

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m playwright install chromium

cp .env.example .env      # then fill it in, see below
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --port 8020
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # point NEXT_PUBLIC_API_BASE at the backend
npm run dev
```

Open http://localhost:3000

### Environment

```bash
MODEL_PROVIDER=groq            # or bedrock
GROQ_API_KEY=
DATABASE_URL=                  # postgres connection string
SESSION_SECRET=                # any long random string

# optional, everything falls back to local files or a log
IMAGEKIT_PRIVATE_KEY=          # document storage
SMTP_HOST=                     # email verification codes
TWILIO_ACCOUNT_SID=            # whatsapp delivery
```

**Nothing is required beyond a database and one model key.** Without ImageKit, documents save locally. Without SMTP, verification codes go to `data/emails.log`. Without Twilio, messages go to a file. The project runs for anyone who clones it.

### Loading exam data

```bash
.venv/Scripts/python -m scripts.refresh_notices     # download official PDFs
.venv/Scripts/python -m scripts.classify_cached     # notification or tender?
.venv/Scripts/python -m scripts.refresh_calendar    # SSC exam calendar
.venv/Scripts/python -m scripts.process_document    # read the rules out
.venv/Scripts/python -m scripts.nightly             # one agent run
```

Cached PDFs are committed on purpose. Government websites move pages without warning, and nothing here should depend on one being awake.

### Tests

```bash
cd backend
.venv/Scripts/python -m pytest tests/ -q
```

159 tests. They never send a real email — a fixture replaces the mailer for the whole suite.

---

## Being straight about the limits

- **MPSC publishes scanned images.** Their notifications are photographs of paper with no extractable text. Those exams appear in the Radar with their real title, date and official link, marked plainly as unread. Reading them needs a vision model.
- **The "When I was wrong" page is labelled.** We have read one version of each notification so far, so that screen says in plain words that the earlier reading was made to demonstrate the behaviour. The comparison code is the same either way.
- **Five sources, not fifty.** SSC, UPSC, IBPS, MPSC and the SSC exam calendar. Adding a sixth is a small, documented file.
- **UPSC recruitment advertisements list many posts** with different rules each. Sarathi handles single-rule exam notifications well and says so when it cannot read a multi-post advert cleanly.

## Licence

MIT. See [LICENSE](LICENSE).
