"""Conservative offline approvals. Broader/ambiguous candidates go to Gemini."""
import re

VERSION = "rules-4"
DIRECT = re.compile(r"\b(?:mechanical (?:and|&) aerospace engineering|(?:mechanical|aerospace|aeronautical) engineering|MAE department|department of MAE)\b", re.I)
TEAMS = re.compile(r"\b(?:EcoCAR|Sunseeker|Bronco Racing|Western Aerospace|Western Aerospace Launch Initiative)\b", re.I)
LOCAL = re.compile(r"\b(?:Western Michigan|WMU|Broncos?)\b", re.I)
# Affirmative relationships, rather than three unrelated keywords in a sentence.
AFFILIATION = re.compile(
    r"\b(?:WMU|Western Michigan(?: University)?)(?:'s|\u2019s)?\s+"
    r"(?:mechanical (?:and|&) aerospace|mechanical|aerospace|aeronautical) engineering\s+"
    r"(?:students?|professors?|faculty|alumn\w*|researchers?|department|chair|majors?)\b|"
    r"\b(?:degree|bachelor(?:'s|\u2019s)?|master(?:'s|\u2019s)?|Ph\.?D)\s+in\s+"
    r"(?:mechanical (?:and|&) aerospace|mechanical|aerospace|aeronautical) engineering\s+"
    r"(?:at|from)\s+Western Michigan(?: University)?\b|"
    r"\b(?:mechanical (?:and|&) aerospace|mechanical|aerospace|aeronautical) engineering\s+"
    r"at\s+Western Michigan(?: University)?\b", re.I)
AMBIGUOUS = re.compile(r"\b(?:not|never|no longer|doesn't|does not|visiting|visitor|fraternity|sorority|guest|formerly)\b", re.I)
OPPORTUNITY = re.compile(r"\b(?:career fair|speaker series|workshop|internship|scholarship|research opportunit\w*|mentoring|networking|design conference)\b", re.I)
AUDIENCE = re.compile(r"\b(?:all (?:engineering |CEAS )?students|all (?:engineering )?majors|students (?:from|of) all disciplines|open to (?:all|the public)|all are welcome)\b", re.I)
FOREIGN = re.compile(r"\b(?:at|of|from) (?!Western Michigan)(?:the )?(?:University (?:of|in)\b|[A-Z][A-Za-z.'&-]*(?: [A-Z][A-Za-z.'&-]*){0,5} (?:University|Institute)\b)")
POSSIBLE = re.compile(r"\b(?:engineer\w*|mechanical|aerospace|MAE|propulsion|robot\w*|Sunseeker|EcoCAR|Bronco Racing|WALI|scholarship\w*|internship\w*|career fair|student opportunit\w*|research opportunit\w*|mentoring)\b", re.I)


def classify(item, content):
    if not POSSIBLE.search(item["title"] + " " + content):
        return {"id": item["id"], "relevant": False, "reason": "No engineering affiliation or student opportunity evidence in source", "method": VERSION}
    if item.get("url", "").startswith("https://wmich.edu/aviation/"):
        return None
    # Inspect sentence-sized context: an unrelated university's MAE department
    # elsewhere in an article is not evidence of a WMU affiliation.
    # A credential buried in an unrelated campus roundup is not an automatic
    # approval. Such later mentions go to AI for a centrality judgment.
    sentences = re.split(r"(?<=[.!?])\s+|\n", item["title"] + "\n" + "\n".join(content.splitlines()[:3]))
    for i, sentence in enumerate(sentences):
        context = " ".join(sentences[max(0, i - 1):i + 2])
        if AFFILIATION.search(sentence) and not AMBIGUOUS.search(context):
            # Foreign institution affiliations in a sentence need AI disambiguation.
            if FOREIGN.search(sentence):
                continue
            return {"id": item["id"], "relevant": True, "reason": "Explicit WMU mechanical/aerospace engineering affiliation", "method": VERSION}
        if TEAMS.search(sentence) and LOCAL.search(sentence) and not AMBIGUOUS.search(context) and not FOREIGN.search(sentence):
            return {"id": item["id"], "relevant": True, "reason": "Identifiable WMU engineering student team", "method": VERSION}
    if item.get("url", "").startswith("https://wmich.edu/engineer/") and OPPORTUNITY.search(item["title"]) and AUDIENCE.search(content):
        return {"id": item["id"], "relevant": True, "reason": "Official CEAS opportunity with inclusive student/public audience", "method": VERSION}
    return None
