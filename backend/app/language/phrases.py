from __future__ import annotations

from enum import StrEnum


class Language(StrEnum):
    ENGLISH = "en"
    HINDI = "hi"


PHRASES: dict[str, dict[Language, str]] = {
    "bucket.apply_now": {
        Language.ENGLISH: "You can apply now",
        Language.HINDI: "आप अभी आवेदन कर सकते हैं",
    },
    "bucket.coming_soon": {
        Language.ENGLISH: "You can apply, form not open yet",
        Language.HINDI: "आप आवेदन कर सकते हैं, फॉर्म अभी खुला नहीं है",
    },
    "bucket.not_yet": {
        Language.ENGLISH: "Not yet",
        Language.HINDI: "अभी नहीं",
    },
    "bucket.not_for_you": {
        Language.ENGLISH: "Not for you",
        Language.HINDI: "आपके लिए नहीं",
    },
    "bucket.closed_for_now": {
        Language.ENGLISH: "Closed for now, it runs again",
        Language.HINDI: "अभी बंद है, यह दोबारा आएगा",
    },
    "bucket.unknown": {
        Language.ENGLISH: "We could not check this one",
        Language.HINDI: "हम इसकी जाँच नहीं कर सके",
    },
    "layer.central": {
        Language.ENGLISH: "Central government - open to every Indian",
        Language.HINDI: "केंद्र सरकार - हर भारतीय के लिए खुला",
    },
    "layer.your_state": {
        Language.ENGLISH: "Your state",
        Language.HINDI: "आपका राज्य",
    },
    "layer.your_city": {
        Language.ENGLISH: "Your city and district",
        Language.HINDI: "आपका शहर और ज़िला",
    },
    "layer.open_to_all_states": {
        Language.ENGLISH: "Other states, open to everyone",
        Language.HINDI: "दूसरे राज्य, सबके लिए खुले",
    },
    "layer.another_state": {
        Language.ENGLISH: "Another state - needs their domicile",
        Language.HINDI: "दूसरा राज्य - वहाँ का निवास प्रमाण चाहिए",
    },
    "relaxation.extra_years": {
        Language.ENGLISH: "You get {years} extra years because you are {category}.",
        Language.HINDI: "आप {category} हैं, इसलिए आपको {years} साल की छूट मिलती है।",
    },
    "age.fine": {
        Language.ENGLISH: "Your age is fine. You are {age} and the limit for you is {limit}.",
        Language.HINDI: "आपकी उम्र ठीक है। आप {age} के हैं और आपके लिए सीमा {limit} है।",
    },
    "age.too_young": {
        Language.ENGLISH: "You are {age}. This exam needs at least {minimum}. You can apply from {when}.",
        Language.HINDI: "आप {age} के हैं। इस परीक्षा के लिए कम से कम {minimum} चाहिए। आप {when} से आवेदन कर सकते हैं।",
    },
    "age.too_old": {
        Language.ENGLISH: "You are {age}. The limit for you is {limit}. This exam is closed to you permanently.",
        Language.HINDI: "आप {age} के हैं। आपके लिए सीमा {limit} है। यह परीक्षा अब आपके लिए हमेशा के लिए बंद है।",
    },
    "domicile.blocked": {
        Language.ENGLISH: "This one is only for people from {state}. You are from {your_state}.",
        Language.HINDI: "यह सिर्फ़ {state} के लोगों के लिए है। आप {your_state} से हैं।",
    },
    "deadline.days_left": {
        Language.ENGLISH: "{exam}: {days} days left to apply, closes {when}.",
        Language.HINDI: "{exam}: आवेदन के लिए {days} दिन बचे हैं, {when} को बंद होगा।",
    },
    "deadline.today": {
        Language.ENGLISH: "{exam}: last day to apply is today.",
        Language.HINDI: "{exam}: आवेदन का आज आख़िरी दिन है।",
    },
    "fee.you_pay_less": {
        Language.ENGLISH: "You pay Rs {yours} instead of Rs {others}. That is Rs {saved} less.",
        Language.HINDI: "आप {others} रुपये की जगह {yours} रुपये देंगे। यानी {saved} रुपये कम।",
    },
    "fee.free": {
        Language.ENGLISH: "You do not have to pay the fee for this exam.",
        Language.HINDI: "इस परीक्षा के लिए आपको फीस नहीं देनी है।",
    },
    "journal.silent": {
        Language.ENGLISH: "Nothing needed your attention.",
        Language.HINDI: "आपके ध्यान देने लायक कुछ नहीं था।",
    },
    "journal.checks_run": {
        Language.ENGLISH: "{checks} checks run, {messages} messages sent.",
        Language.HINDI: "{checks} जाँच की गईं, {messages} संदेश भेजे गए।",
    },
    "corrigendum.i_was_wrong": {
        Language.ENGLISH: "I was wrong. Here is the correction.",
        Language.HINDI: "मैं ग़लत था। यह रहा सुधार।",
    },
    "unreadable.scanned": {
        Language.ENGLISH: "This notification is a scanned image. Please read it yourself.",
        Language.HINDI: "यह सूचना एक स्कैन की गई तस्वीर है। कृपया इसे ख़ुद पढ़ें।",
    },
}


def say(key: str, language: Language = Language.ENGLISH, **values: object) -> str:
    entry = PHRASES.get(key)
    if entry is None:
        return key
    template = entry.get(language) or entry[Language.ENGLISH]
    try:
        return template.format(**values)
    except KeyError:
        return template
