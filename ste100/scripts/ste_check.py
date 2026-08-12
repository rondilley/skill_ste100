#!/usr/bin/env python3
"""ste_check.py - mechanical ASD-STE100 (Issue 9) checker.

Checks text or Markdown against the STE writing rules that a machine can test
reliably. It does not replace judgement: rules about one topic per sentence,
correct approved meanings, and correct technical-noun selection stay with the
writer.

Usage:
    python3 ste_check.py FILE [FILE ...]
    cat draft.md | python3 ste_check.py -
    python3 ste_check.py --json report.md
    python3 ste_check.py --allow myterms.txt report.md
    python3 ste_check.py --max-info 40 report.md

Exit codes:
    0  no errors
    1  one or more errors (warnings and info do not change the exit code)
    2  bad invocation

An allowlist file holds one term per line (# starts a comment). The checker
also reads ./.ste-allow and ./.claude/.ste-allow when they are present.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON_PATH = os.path.join(HERE, "data", "ste_lexicon.json")
TECH_TERMS_PATH = os.path.join(HERE, "data", "tech_terms.txt")

# --------------------------------------------------------------------------
# Static word sets
# --------------------------------------------------------------------------

BE_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am"}
HAVE_FORMS = {"have", "has", "had", "having"}
MODALS = {"can", "cannot", "must", "will", "would", "should", "could", "may", "might", "shall"}

# Rule 3.5: the only approved words in the dictionary with an "-ing" form.
APPROVED_ING = {"lighting", "opening", "routing", "servicing", "mating", "missing",
                "remaining", "something", "during", "nothing", "anything", "everything"}

# Words that end in "ing" but are not verb forms.
ING_NOT_VERBS = {"thing", "string", "ring", "spring", "king", "wing", "sting", "swing",
                 "ceiling", "morning", "evening", "engineering", "meaning", "warning",
                 "bearing", "casing", "housing", "tubing", "wiring", "piping", "coating",
                 "plating", "fitting", "setting", "reading", "heading", "listing",
                 "logging", "monitoring", "phishing", "hardening", "onboarding",
                 "tooling", "training", "briefing", "finding", "findings", "learning",
                 "computing", "networking", "encoding", "indexing", "caching",
                 "sampling", "polling", "queueing", "scheduling", "streaming",
                 "versioning", "sharding", "hashing", "signing", "packaging",
                 "shipping", "handling", "cleaning", "testing", "troubleshooting"}

CONTRACTIONS = re.compile(
    r"\b\w+(?:'|’)(?:t|s|re|ve|ll|d|m)\b|\b(?:can't|won't|don't|isn't|aren't|wasn't|"
    r"weren't|doesn't|didn't|hasn't|haven't|hadn't|shouldn't|wouldn't|couldn't|it's|"
    r"that's|there's|let's|I'm|we're|they're|you're|we'll|I'll|we've|I've)\b",
    re.IGNORECASE)

LATIN_ABBREV = re.compile(r"(?<![\w.])(e\.g\.|i\.e\.|etc\.|viz\.|cf\.|et al\.|N\.B\.|vs\.)",
                          re.IGNORECASE)

GENDERED = {"he", "she", "him", "her", "his", "hers", "himself", "herself",
            "he's", "she's"}

# Words that mark the token after them as a noun. Used to tell a banned verb
# ("do not oil the surface") from the same word used as a technical noun
# ("apply oil to the surface").
DETERMINERS = {
    "the", "a", "an", "this", "these", "that", "those", "its", "their", "your",
    "our", "my", "each", "every", "all", "both", "some", "any", "no", "other",
    "same", "new", "first", "second", "third", "next", "last", "previous",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "many", "more", "most", "several", "of", "with", "in", "on", "for",
    "from", "at", "by", "into", "than",
}

# Numbers and ordinals are technical nouns (rule 1.5, category 9).
NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty",
    "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred",
    "thousand", "million", "billion", "half", "quarter",
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth",
}

# Common irregular past participles, for passive / perfect-tense detection.
IRREGULAR_PP = {
    "been", "begun", "broken", "brought", "built", "bought", "chosen", "come", "done",
    "drawn", "driven", "eaten", "fallen", "felt", "found", "given", "gone", "grown",
    "held", "kept", "known", "laid", "led", "left", "lost", "made", "meant", "met",
    "paid", "put", "read", "run", "said", "seen", "sent", "set", "shown", "shut",
    "sold", "spent", "split", "taken", "taught", "told", "thought", "understood",
    "withdrawn", "written", "cut", "hit", "let", "shot", "spread", "torn", "worn",
}

# Rule 1.5 category 19 and rule 1.12 category 2: computing and security terms that
# are legitimate technical nouns and technical verbs. Extend with an allowlist file.
TECH_TERMS = {
    # nouns
    "ai", "api", "app", "artifact", "artifacts", "authentication", "authorization",
    "backup", "backups", "backlog", "baseline", "binary", "branch", "browser", "buffer",
    "bug", "bugs", "build", "builds", "bookmark", "cache", "callback", "chatbot", "cli",
    "client", "cloud", "cluster", "codebase", "commit", "commits", "compiler", "config",
    "container", "containers", "content", "cookie", "cursor", "cve", "cvss", "daemon",
    "dashboard", "database", "dataset", "debugger", "dependency", "dependencies",
    "deployment", "diff", "directory", "docker", "domain", "driver", "endpoint",
    "endpoints", "environment", "exploit", "exploits", "feature", "features", "field",
    "file", "files", "filesystem", "firewall", "firmware", "framework", "frontend",
    "backend", "function", "functions", "gateway", "git", "handler", "hash", "header",
    "headers", "heap", "host", "hostname", "html", "http", "https", "icon", "ide",
    "index", "indicator", "infrastructure", "interface", "internet", "ioc", "iocs",
    "json", "kernel", "key", "keys", "kubernetes", "laptop", "latency", "library",
    "linter", "log", "logs", "login", "malware", "memory", "metadata", "metric",
    "metrics", "middleware", "migration", "milestone", "module", "modules", "mouse",
    "namespace", "network", "node", "nodes", "operator", "orchestrator", "packet",
    "packets", "parameter", "parameters", "parser", "password", "patch", "patches",
    "path", "payload", "permission", "permissions", "pipeline", "plugin", "port",
    "prompt", "protocol", "proxy", "pull request", "query", "queue", "ransomware",
    "regex", "registry", "release", "repository", "repo", "request", "response",
    "roadmap", "router", "runbook", "runtime", "sandbox", "scan", "schema", "scope",
    "screen", "script", "sdk", "server", "service", "session", "signature", "smartphone",
    "snapshot", "socket", "software", "source", "sprint", "sql", "ssh", "stack",
    "stakeholder", "stakeholders", "storage", "string", "subnet", "syntax", "tablet",
    "telemetry", "template", "tenant", "test suite", "thread", "threat", "throughput",
    "ticket", "timeout", "token", "toolbar", "touchscreen", "traffic", "transcript",
    "tuning", "url", "user", "users", "username", "variable", "vector", "vendor",
    "version", "vlan", "vpn", "vulnerability", "vulnerabilities", "webhook", "workflow",
    "workload", "workspace", "xml", "yaml", "zone",
    # verbs (rule 1.12 category 2)
    "abort", "boot", "click", "close", "commit", "compile", "configure", "copy", "cut",
    "debug", "delete", "deploy", "deselect", "digitize", "disable", "download", "drag",
    "enable", "encrypt", "enter", "erase", "execute", "export", "filter", "format",
    "highlight", "import", "install", "load", "log", "manage", "maximize", "merge",
    "migrate", "minimize", "navigate", "open", "parse", "paste", "patch", "press",
    "print", "process", "provision", "publish", "query", "reboot", "refactor", "render",
    "restart", "roll back", "run", "save", "scan", "scroll", "sort", "store", "swipe",
    "sync", "tap", "type", "upgrade", "upload", "validate", "zoom",
    # forms of the above that regular inflection produces
    "aborts", "aborted", "boots", "booted", "clicks", "clicked", "commits", "committed",
    "compiles", "compiled", "configures", "configured", "copies", "copied", "debugs",
    "debugged", "deletes", "deleted", "deploys", "deployed", "disables", "disabled",
    "downloads", "downloaded", "enables", "enabled", "encrypts", "encrypted", "enters",
    "entered", "executes", "executed", "exports", "exported", "filters", "filtered",
    "formats", "formatted", "imports", "imported", "installs", "installed", "loads",
    "loaded", "logs", "logged", "manages", "managed", "merges", "merged", "migrates",
    "migrated", "opens", "opened", "parses", "parsed", "patches", "patched", "presses",
    "pressed", "processes", "processed", "publishes", "published", "queries", "queried",
    "reboots", "rebooted", "renders", "rendered", "restarts", "restarted", "runs",
    "saves", "saved", "scans", "scanned", "scrolls", "scrolled", "sorts", "sorted",
    "stores", "stored", "syncs", "synced", "updates", "updated", "upgrades", "upgraded",
    "uploads", "uploaded", "validates", "validated",
}

def _load_tech_terms():
    """Technical nouns and technical verbs listed in rules 1.5 and 1.12."""
    if not os.path.exists(TECH_TERMS_PATH):
        return set()
    out = set()
    with open(TECH_TERMS_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip().lower()
            if line and " " not in line:
                out.add(line)
    return out


TECH_TERMS |= _load_tech_terms()


# --------------------------------------------------------------------------
# Finding
# --------------------------------------------------------------------------


class Finding(object):
    __slots__ = ("severity", "rule", "line", "message", "snippet", "suggestion")

    def __init__(self, severity, rule, line, message, snippet="", suggestion=""):
        self.severity = severity
        self.rule = rule
        self.line = line
        self.message = message
        self.snippet = snippet
        self.suggestion = suggestion

    def as_dict(self):
        return {
            "severity": self.severity,
            "rule": self.rule,
            "line": self.line,
            "message": self.message,
            "snippet": self.snippet,
            "suggestion": self.suggestion,
        }


# --------------------------------------------------------------------------
# Masking: keep code, paths, URLs and quoted text out of the prose checks
# --------------------------------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"<?https?://\S+>?|\bwww\.\S+")
MD_LINK_RE = re.compile(r"\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>\s]+>")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
LIST_ITEM_RE = re.compile(r"^\s{0,8}(?:[-*+]|\(?\d+[.)]|\(?[a-zA-Z][.)])\s+")


def mask_line(line):
    """Blank out spans that STE does not govern, keeping character offsets."""
    def blank(m):
        return " " * (m.end() - m.start())
    for rx in (INLINE_CODE_RE, URL_RE, MD_LINK_RE, HTML_TAG_RE):
        line = rx.sub(blank, line)
    return line


def strip_markdown(line):
    """Remove list bullets, heading marks and table pipes from a masked line."""
    line = re.sub(r"^\s{0,8}(?:[-*+]|\(?\d+[.)]|\(?[a-zA-Z][.)])\s+", "", line)
    line = re.sub(r"^\s{0,8}#{1,6}\s+", "", line)
    line = line.replace("|", " ")
    line = re.sub(r"^\s*>+\s*", "", line)
    line = re.sub(r"[*_]{1,3}", "", line)
    return line


# --------------------------------------------------------------------------
# Tokenizing and STE word count
# --------------------------------------------------------------------------

PAREN_RE = re.compile(r"\([^)]*\)")
QUOTE_RE = re.compile(r"[“\"][^”\"]*[”\"]")
NUM_UNIT_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|[A-Za-zµ°][A-Za-z/°]{0,6})\b")
ALLCAPS_RUN_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,}(?:\s+[A-Z][A-Z0-9-]+)+\b")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def count_words(sentence):
    """Word count under rules 8.5 thru 8.7."""
    s = sentence
    s = PAREN_RE.sub(" ONEWORD ", s)          # rule 8.5
    s = QUOTE_RE.sub(" ONEWORD ", s)          # rule 8.6 item 5
    s = ALLCAPS_RUN_RE.sub(" ONEWORD ", s)    # rule 8.6 item 5 (placards, labels)
    s = NUM_UNIT_RE.sub(" ONEWORD ", s)       # rule 8.6 item 2
    n = 0
    for tok in re.findall(r"\S+", s):
        # A hyphenated group counts as one word (rule 8.7).
        if tok.strip(".,:;!?()[]{}\"'“”…"):
            n += 1
    return n


def tokens_of(text):
    """Prose word tokens, with the spans that STE exempts already removed."""
    t = PAREN_RE.sub(" ", text)
    t = QUOTE_RE.sub(" ", t)
    t = ALLCAPS_RUN_RE.sub(" ", t)
    out = []
    for raw in re.findall(r"\S+", t):
        core = raw.strip(".,:;!?()[]{}‘’“”…")
        if not core:
            continue
        out.append(core)
    return out


SENT_SPLIT_RE = re.compile(r"(?<=[.!?:])\s+")
ABBREV_TAIL_RE = re.compile(r"\b(?:No|Fig|Sec|Ref|approx|vs|Dr|Mr|Ms|St|Inc|Ltd|Jr|Sr|"
                            r"[A-Z])\.$")


def split_sentences(text):
    """Split into sentences. A colon ends a sentence under rule 8.4."""
    parts = SENT_SPLIT_RE.split(text)
    merged = []
    for p in parts:
        if merged and ABBREV_TAIL_RE.search(merged[-1]):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return [p.strip() for p in merged if p.strip()]


# --------------------------------------------------------------------------
# Checker
# --------------------------------------------------------------------------


class SteChecker(object):

    def __init__(self, lexicon, allow=None, check_vocab=True):
        self.approved = lexicon["approved"]
        self.not_approved = lexicon["not_approved"]
        self.base_pos = lexicon["base_pos"]
        self.allow = set(a.lower() for a in (allow or []))
        self.check_vocab = check_vocab
        self.findings = []

    # -- helpers ---------------------------------------------------------

    def add(self, *a, **kw):
        self.findings.append(Finding(*a, **kw))

    def is_exempt(self, token):
        """True when STE does not govern this token (rules 1.5, 1.12, 8.6)."""
        low = token.lower().strip("-")
        if not low or len(low) == 1:
            return True
        if low in self.allow or low in TECH_TERMS or low in NUMBER_WORDS:
            return True
        if any(ch.isdigit() for ch in token):
            return True                                   # alphanumeric identifier
        if any(ch in token for ch in "._/\\:@#$%&+=~^"):
            return True                                   # path, address, identifier
        if token.isupper() and len(token) >= 2:
            return True                                   # abbreviation / acronym
        if re.search(r"[a-z][A-Z]", token):
            return True                                   # CamelCase identifier
        if token[0].isupper() and not token.isupper():
            return True                                   # proper noun (rule 8.6 item 7)
        return False

    def verb_stem(self, ing_word):
        """Candidate base forms for an -ing word."""
        w = ing_word.lower()
        if not w.endswith("ing") or len(w) < 6:
            return []
        root = w[:-3]
        cands = [root, root + "e"]
        if len(root) > 2 and root[-1] == root[-2]:
            cands.append(root[:-1])
        return cands

    def looks_like_verb(self, word):
        low = word.lower()
        return "v" in self.base_pos.get(low, []) or low in TECH_TERMS

    def is_past_participle(self, word):
        low = word.lower()
        if low in IRREGULAR_PP:
            return True
        if not low.endswith("ed") or len(low) < 5:
            return False
        for cand in (low[:-2], low[:-1], low[:-3] + "y" if low.endswith("ied") else low[:-2]):
            if cand in self.base_pos or cand in TECH_TERMS:
                return True
        return low in self.approved or low in self.not_approved

    def looks_imperative(self, sentence):
        toks = tokens_of(sentence)
        if not toks:
            return False
        first = toks[0].lower()
        if first in ("do", "make", "put", "set", "use", "refer", "obey", "install",
                     "remove", "start", "stop", "open", "close", "run", "check"):
            return True
        if first in ("if", "when", "before", "after", "while"):
            for i, t in enumerate(toks):
                if t.endswith(","):
                    nxt = toks[i + 1].lower() if i + 1 < len(toks) else ""
                    return "v" in self.base_pos.get(nxt, []) or nxt in TECH_TERMS
        return "v" in self.base_pos.get(first, []) and first not in BE_FORMS

    # -- line-level checks -----------------------------------------------

    def check_line(self, lineno, raw, masked):
        text = strip_markdown(masked)

        # Rule 8.1 - no semicolon
        for m in re.finditer(r";", text):
            self.add("error", "8.1", lineno,
                     "The semicolon is not permitted. Write two sentences.",
                     snippet=self._around(text, m.start()))

        # Rule 4.2 - no contractions
        for m in CONTRACTIONS.finditer(text):
            tok = m.group(0)
            if tok.lower().endswith("'s") and not tok.lower() in ("it's", "that's",
                                                                  "there's", "let's",
                                                                  "he's", "she's"):
                continue                                   # possessive is permitted (GR-8)
            self.add("error", "4.2", lineno,
                     "Contractions are not permitted. Write the words in full.",
                     snippet=tok)

        # GR-6 - no Latin abbreviations
        for m in LATIN_ABBREV.finditer(text):
            self.add("warn", "GR-6", lineno,
                     "Latin abbreviations are not recommended. Use English words.",
                     snippet=m.group(0),
                     suggestion={"e.g.": "for example", "i.e.": "that is",
                                 "etc.": "and so on", "vs.": "compared with"}
                     .get(m.group(0).lower(), "an English phrase"))

        toks = tokens_of(text)
        low = [t.lower().strip("-") for t in toks]

        # GR-7 - gender-neutral language
        prereported = set(t for t in low if t in GENDERED)
        for t in low:
            if t in GENDERED:
                self.add("error", "GR-7", lineno,
                         "Gender-specific pronouns are not permitted. Use \"you\", "
                         "\"we\", or the noun.", snippet=t)

        flagged = set()          # words already reported by a grammar rule
        for i, t in enumerate(low):
            nxt = low[i + 1] if i + 1 < len(low) else ""

            # Rule 3.4 - no perfect tenses
            if t in HAVE_FORMS and nxt and self.is_past_participle(nxt):
                self.add("error", "3.4", lineno,
                         "Perfect tense is not permitted. Use the simple past tense.",
                         snippet="%s %s" % (t, nxt))
                flagged.add(t)
                flagged.add(nxt)

            # Rule 3.2 / 3.5 - no progressive tenses
            if t in BE_FORMS and nxt.endswith("ing") and nxt not in APPROVED_ING:
                if any(self.looks_like_verb(c) for c in self.verb_stem(nxt)):
                    self.add("error", "3.5", lineno,
                             "Progressive tense is not permitted. Use the simple "
                             "present or simple past tense.",
                             snippet="%s %s" % (t, nxt))
                    flagged.add(t)
                    flagged.add(nxt)
                    continue

            # Rule 3.6 - active voice
            if t in BE_FORMS and nxt and self.is_past_participle(nxt):
                by = " by " in text[max(0, text.lower().find(nxt)):].lower()[:80]
                self.add("error" if by else "warn", "3.6", lineno,
                         "This looks like the passive voice. Use the active voice, or "
                         "the imperative form in a work step.",
                         snippet="%s %s" % (t, nxt))
                flagged.add(t)
                flagged.add(nxt)

            # Rule 3.5 - bare -ing forms
            if (t.endswith("ing") and t not in APPROVED_ING and t not in ING_NOT_VERBS
                    and t not in self.allow and t not in TECH_TERMS
                    and len(t) > 5 and not self.is_exempt(toks[i])):
                if any(self.looks_like_verb(c) for c in self.verb_stem(t)):
                    self.add("warn", "3.5", lineno,
                             "The \"-ing\" form is permitted only in a technical noun. "
                             "Rewrite with a simple tense.", snippet=t)
                    flagged.add(t)

        # Vocabulary - rules 1.1 thru 1.3
        if self.check_vocab:
            skip = flagged | prereported | BE_FORMS | HAVE_FORMS | MODALS
            for i, t in enumerate(low):
                if t in skip or self.is_exempt(toks[i]):
                    continue
                if t in self.approved:
                    continue
                entry = self.not_approved.get(t)
                if entry:
                    alts = ", ".join(entry["alt"])
                    pos = entry["pos"]
                    prev = low[i - 1] if i > 0 else ""
                    prev_pos = self.base_pos.get(prev, [])
                    noun_position = (
                        prev in DETERMINERS
                        or "adj" in prev_pos
                        or self.is_past_participle(prev)
                        or prev in TECH_TERMS
                        or ("v" in prev_pos and prev not in BE_FORMS
                            and prev not in HAVE_FORMS and prev not in MODALS))

                    if pos == ["v"] and noun_position:
                        # Banned as a verb only, and here it fills a noun slot.
                        # Rules 1.5 and 1.6 permit that.
                        self.add("info", "1.6", lineno,
                                 "\"%s\" is banned as a verb but is permitted as a "
                                 "technical noun. Confirm the part of speech." % t,
                                 snippet=t, suggestion=alts)
                    elif "n" in pos and noun_position:
                        # Rule 1.6: a banned noun is still usable when it fits a
                        # technical-noun category, so this needs a decision.
                        self.add("warn", "1.6", lineno,
                                 "\"%s\" is not approved as a general noun. Keep it "
                                 "only if it fits a technical-noun category (rule "
                                 "1.5)." % t, snippet=t, suggestion=alts)
                    else:
                        self.add("error", "1.1", lineno,
                                 "\"%s\" is not approved in the STE dictionary." % t,
                                 snippet=t,
                                 suggestion=alts or "rewrite with approved words")
                else:
                    self.add("info", "1.1", lineno,
                             "\"%s\" is not in the STE dictionary. Keep it only if it "
                             "is a technical noun (rule 1.5) or a technical verb "
                             "(rule 1.12)." % t, snippet=t)

    def _around(self, text, pos, width=40):
        a = max(0, pos - width // 2)
        return text[a:a + width].strip()

    # -- block-level checks ----------------------------------------------

    def check_block(self, lines, start_lineno):
        """lines: masked, markdown-stripped text lines of one paragraph."""
        blob = " ".join(l.strip() for l in lines if l.strip())
        if not blob:
            return
        sentences = split_sentences(blob)

        # Rule 6.6 - paragraph length
        if len(sentences) > 6:
            self.add("error", "6.6", start_lineno,
                     "This paragraph has %d sentences. Use a maximum of six."
                     % len(sentences),
                     snippet=sentences[0][:60])

        # Rules 5.1 and 6.3 - sentence length
        for s in sentences:
            n = count_words(s)
            imperative = self.looks_imperative(s)
            limit = 20 if imperative else 25
            if n > limit:
                self.add("error", "5.1" if imperative else "6.3", start_lineno,
                         "This sentence has %d words. The limit is %d for %s writing."
                         % (n, limit, "procedural" if imperative else "descriptive"),
                         snippet=s[:80])

    # -- driver ----------------------------------------------------------

    def check_text(self, text):
        self.findings = []
        raw_lines = text.splitlines()
        in_fence = False
        block, block_start = [], 1

        for idx, raw in enumerate(raw_lines, start=1):
            if FENCE_RE.match(raw):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.match(r"^\s*\|?\s*[-:| ]+\s*\|?\s*$", raw) and "|" in raw:
                continue                                    # markdown table rule
            masked = mask_line(raw)
            if TABLE_ROW_RE.match(raw):
                # Each cell of a table is its own unit of text.
                if block:
                    self.check_block(block, block_start)
                    block = []
                self.check_line(idx, raw, masked)
                for cell in masked.strip().strip("|").split("|"):
                    cell = strip_markdown(cell).strip()
                    if cell:
                        self.check_block([cell], idx)
                continue
            if raw.strip():
                self.check_line(idx, raw, masked)
                # Rule 8.4: each item of a vertical list counts as a sentence.
                if LIST_ITEM_RE.match(raw) and block:
                    self.check_block(block, block_start)
                    block = []
                if not block:
                    block_start = idx
                block.append(strip_markdown(masked))
            else:
                if block:
                    self.check_block(block, block_start)
                block = []
        if block:
            self.check_block(block, block_start)
        return self.findings


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

ORDER = {"error": 0, "warn": 1, "info": 2}


def report_text(path, findings, max_info):
    errs = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]
    infos = [f for f in findings if f.severity == "info"]

    out = []
    out.append("=" * 68)
    out.append("STE-100 check: %s" % path)
    out.append("%d error(s), %d warning(s), %d word(s) to examine"
               % (len(errs), len(warns), len(infos)))
    out.append("=" * 68)

    for group, title in ((errs, "ERRORS"), (warns, "WARNINGS")):
        if not group:
            continue
        out.append("")
        out.append(title)
        out.append("-" * len(title))
        for f in sorted(group, key=lambda x: (x.line, x.rule)):
            line = "  line %-5d rule %-5s %s" % (f.line, f.rule, f.message)
            out.append(line)
            if f.snippet:
                out.append("        text: %s" % f.snippet)
            if f.suggestion:
                out.append("        use : %s" % f.suggestion)

    if infos:
        out.append("")
        out.append("WORDS TO EXAMINE (keep only as technical nouns or technical verbs)")
        out.append("-" * 64)
        seen = {}
        for f in infos:
            seen.setdefault(f.snippet, []).append(f.line)
        items = sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        for word, lines in items[:max_info]:
            out.append("  %-24s lines %s" % (word, ", ".join(str(x) for x in lines[:8])))
        if len(items) > max_info:
            out.append("  ... and %d more" % (len(items) - max_info))
    out.append("")
    return "\n".join(out)


def load_allow(paths):
    words = []
    for p in paths:
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    line = line.split("#", 1)[0].strip()
                    if line:
                        words.append(line)
    return words


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASD-STE100 mechanical checker")
    ap.add_argument("files", nargs="+", help="files to check, or - for stdin")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--allow", action="append", default=[],
                    help="allowlist file of project technical terms")
    ap.add_argument("--no-vocab", action="store_true",
                    help="skip the dictionary check; test the writing rules only")
    ap.add_argument("--max-info", type=int, default=30,
                    help="maximum distinct words to show under WORDS TO EXAMINE")
    args = ap.parse_args(argv)

    if not os.path.exists(LEXICON_PATH):
        sys.stderr.write("lexicon not found: %s\nRun build_lexicon.py first.\n"
                         % LEXICON_PATH)
        return 2
    with open(LEXICON_PATH, encoding="utf-8") as fh:
        lexicon = json.load(fh)

    allow = load_allow(list(args.allow) + [".ste-allow", ".claude/.ste-allow"])
    checker = SteChecker(lexicon, allow=allow, check_vocab=not args.no_vocab)

    total_errors = 0
    results = []
    for path in args.files:
        if path == "-":
            text, label = sys.stdin.read(), "<stdin>"
        else:
            if not os.path.exists(path):
                sys.stderr.write("no such file: %s\n" % path)
                return 2
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            label = path
        findings = checker.check_text(text)
        total_errors += sum(1 for f in findings if f.severity == "error")
        if args.json:
            results.append({"file": label,
                            "findings": [f.as_dict() for f in findings]})
        else:
            print(report_text(label, findings, args.max_info))

    if args.json:
        print(json.dumps(results, indent=2))
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
