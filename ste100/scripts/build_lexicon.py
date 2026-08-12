#!/usr/bin/env python3
"""Build the compact STE lexicon used by ste_check.py.

Reads ste_dictionary_full.csv (ASD-STE100 Issue 9, Part 2) and writes
ste_lexicon.json with:
  approved      : {surface_form_lower: [parts_of_speech]}
  not_approved  : {surface_form_lower: {"pos": [...], "alt": [...]}}
  base_pos      : {base_word_lower: [parts_of_speech]}

Run this again only if the source CSVs change.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def plural_forms(noun):
    """Regular English plural forms for an approved singular noun."""
    n = noun.lower()
    out = set()
    if re.search(r"(s|x|z|ch|sh)$", n):
        out.add(n + "es")
    elif re.search(r"[^aeiou]y$", n):
        out.add(n[:-1] + "ies")
    elif n.endswith("f"):
        out.add(n[:-1] + "ves")
        out.add(n + "s")
    elif n.endswith("fe"):
        out.add(n[:-2] + "ves")
        out.add(n + "s")
    else:
        out.add(n + "s")
    return out


def verb_forms(base):
    """Regular third-person / past forms, used only when the CSV omits them."""
    b = base.lower()
    out = set()
    if re.search(r"(s|x|z|ch|sh|o)$", b):
        out.add(b + "es")
    elif re.search(r"[^aeiou]y$", b):
        out.add(b[:-1] + "ies")
    else:
        out.add(b + "s")
    if b.endswith("e"):
        out.add(b + "d")
    elif re.search(r"[^aeiou]y$", b):
        out.add(b[:-1] + "ied")
    else:
        out.add(b + "ed")
    return out


# The dictionary writes some irregular verbs in prose ("IS, WAS, (also ARE, WERE)")
# and omits participles that rule 3.2 and rule 3.3 permit. Supply them here.
IRREGULAR_SUPPLEMENT = {
    "be": ["is", "are", "was", "were", "been", "am"],
    "have": ["has", "had"],
    "do": ["does", "did", "done"],
    "can": ["could"],
    "get": ["gets", "got", "gotten"],
    "go": ["goes", "went", "gone"],
    "see": ["sees", "saw", "seen"],
    "make": ["makes", "made"],
    "become": ["becomes", "became"],
    "give": ["gives", "gave", "given"],
    "keep": ["keeps", "kept"],
    "hold": ["holds", "held"],
    "let": ["lets"],
    "put": ["puts"],
    "read": ["reads"],
    "send": ["sends", "sent"],
    "set": ["sets"],
    "show": ["shows", "showed", "shown"],
    "tell": ["tells", "told"],
    "think": ["thinks", "thought"],
    "find": ["finds", "found"],
    "come": ["comes", "came"],
    "cut": ["cuts"],
    "know": ["knows", "knew", "known"],
    "leave": ["leaves", "left"],
    "lose": ["loses", "lost"],
    "take": ["takes", "took", "taken"],
    "write": ["writes", "wrote", "written"],
    "break": ["breaks", "broke", "broken"],
    "build": ["builds", "built"],
    "bring": ["brings", "brought"],
    "fall": ["falls", "fell", "fallen"],
    "feel": ["feels", "felt"],
    "hit": ["hits"],
    "wear": ["wears", "wore", "worn"],
}


def split_forms(raw):
    """'IS, WAS, (also ARE, WERE)' -> ['is', 'was', 'are', 'were']"""
    raw = re.sub(r"\balso\b", " ", raw or "", flags=re.I)
    raw = raw.replace("(", " ").replace(")", " ")
    return [f.strip().lower() for f in re.split(r"[,/]", raw) if f.strip()]


def split_alts(raw):
    """'GO (v) | STOP (v)' -> ['go (v)', 'stop (v)']"""
    if not raw:
        return []
    return [a.strip() for a in raw.split("|") if a.strip()]


def main():
    src = os.path.join(DATA, "ste_dictionary_full.csv")
    approved = {}
    not_approved = {}
    base_pos = {}

    with open(src, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            word = (row["word"] or "").strip()
            if not word or " " in word:
                continue
            pos = (row["part_of_speech"] or "").strip()
            low = word.lower()
            base_pos.setdefault(low, [])
            if pos and pos not in base_pos[low]:
                base_pos[low].append(pos)

            if row["status"].startswith("STE"):
                forms = {low} | set(split_forms(row.get("other_forms")))
                if pos == "v":
                    forms |= set(IRREGULAR_SUPPLEMENT.get(low, []))
                if pos == "n":
                    forms |= plural_forms(low)
                elif pos == "v" and not row.get("other_forms"):
                    forms |= verb_forms(low)
                for f in forms:
                    approved.setdefault(f, [])
                    if pos and pos not in approved[f]:
                        approved[f].append(pos)
            else:
                alts = split_alts(row.get("approved_alternatives"))
                entry = not_approved.setdefault(low, {"pos": [], "alt": []})
                if pos and pos not in entry["pos"]:
                    entry["pos"].append(pos)
                for a in alts:
                    if a not in entry["alt"]:
                        entry["alt"].append(a)
                # Inflections of a banned word are also banned.
                extra = set(split_forms(row.get("other_forms")))
                if pos == "v":
                    extra |= verb_forms(low)
                elif pos == "n":
                    extra |= plural_forms(low)
                for f in extra:
                    if f == low:
                        continue
                    e = not_approved.setdefault(f, {"pos": [], "alt": []})
                    if pos and pos not in e["pos"]:
                        e["pos"].append(pos)
                    for a in alts:
                        if a not in e["alt"]:
                            e["alt"].append(a)

    # An approved form always wins over a derived not-approved form.
    for f in list(not_approved):
        if f in approved:
            del not_approved[f]

    out = {
        "source": "ASD-STE100 Issue 9 (January 2025), Part 2 - Dictionary",
        "approved": {k: sorted(v) for k, v in sorted(approved.items())},
        "not_approved": {k: not_approved[k] for k in sorted(not_approved)},
        "base_pos": {k: sorted(v) for k, v in sorted(base_pos.items())},
    }
    dest = os.path.join(DATA, "ste_lexicon.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    print(
        "wrote %s: %d approved forms, %d not-approved forms"
        % (dest, len(out["approved"]), len(out["not_approved"])),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
