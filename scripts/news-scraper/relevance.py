"""Conservative offline approvals. Broader/ambiguous candidates go to Gemini."""
import re

VERSION = "rules-2"
DIRECT = re.compile(r"\b(?:mechanical (?:and|&) aerospace engineering|(?:mechanical|aerospace|aeronautical) engineering|MAE department|department of MAE)\b", re.I)
TEAMS = re.compile(r"\b(?:EcoCAR|Sunseeker|Bronco Racing|Western Aerospace|Western Aerospace Launch Initiative)\b", re.I)
LOCAL = re.compile(r"\b(?:Western Michigan|WMU|Broncos?)\b", re.I)
PERSON = re.compile(r"\b(?:students?|professors?|faculty|alumn\w*|researchers?|department|program|degree|bachelor|master|Ph\.?D|engineering)\b", re.I)
OPPORTUNITY = re.compile(r"\b(?:career fair|speaker series|workshop|internship|scholarship|research opportunit\w*|mentoring|networking|design conference)\b", re.I)
AUDIENCE = re.compile(r"\b(?:all (?:engineering |CEAS )?students|all (?:engineering )?majors|students (?:from|of) all disciplines|open to (?:all|the public)|all are welcome)\b", re.I)
FOREIGN = re.compile(r"\b(?:at|of|from) (?!Western Michigan)(?:the )?(?:University (?:of|in)\b|[A-Z][A-Za-z.'&-]*(?: [A-Z][A-Za-z.'&-]*){0,5} (?:University|Institute)\b)")
POSSIBLE = re.compile(r"\b(?:engineer\w*|mechanical|aerospace|MAE|propulsion|robot\w*|Sunseeker|EcoCAR|Bronco Racing|WALI|scholarship\w*|internship\w*|career fair|student opportunit\w*|research opportunit\w*|mentoring)\b", re.I)


def classify(item, content):
    # Inspect sentence-sized context: an unrelated university's MAE department
    # elsewhere in an article is not evidence of a WMU affiliation.
    # A credential buried in an unrelated campus roundup is not an automatic
    # approval. Such later mentions go to AI for a centrality judgment.
    sentences = re.split(r"(?<=[.!?])\s+|\n", item["title"] + "\n" + "\n".join(content.splitlines()[:3]))
    for i, sentence in enumerate(sentences):
        context = " ".join(sentences[max(0, i - 1):i + 2])
        if DIRECT.search(sentence) and PERSON.search(sentence) and LOCAL.search(context):
            # Foreign institution affiliations in a sentence need AI disambiguation.
            if FOREIGN.search(sentence):
                continue
            return {"id": item["id"], "relevant": True, "reason": "Explicit WMU mechanical/aerospace engineering affiliation", "method": VERSION}
        if TEAMS.search(sentence) and LOCAL.search(context):
            return {"id": item["id"], "relevant": True, "reason": "Identifiable WMU engineering student team", "method": VERSION}
    if item["url"].startswith("https://wmich.edu/engineer/") and OPPORTUNITY.search(item["title"]) and AUDIENCE.search(content):
        return {"id": item["id"], "relevant": True, "reason": "Official CEAS opportunity with inclusive student/public audience", "method": VERSION}
    if not POSSIBLE.search(item["title"] + " " + content):
        return {"id": item["id"], "relevant": False, "reason": "No engineering affiliation or student opportunity evidence in source", "method": VERSION}
    return None
