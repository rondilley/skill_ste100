---
name: ste100
description: Enforce ASD-STE100 Simplified Technical English in everything Claude says to the user in the command window and in every project report artifact Claude produces. Use for all status updates, progress reports, findings, error reports, explanations, and answers given back to the user, and for every generated report, runbook, README, design doc, analysis, summary, changelog, or other project document. Also use when the user asks to check, rewrite, or validate text against STE100, Simplified Technical English, ASD-STE100, controlled English, or plain technical English. Do NOT use for articles, blog posts, books, short stories, marketing copy, poetry, personal essays, social posts, or any writing meant to publish under a byline.
license: The skill is provided as-is. ASD-STE100 is copyright ASD (Aerospace, Security and Defence Industries Association of Europe) and is a registered EU trademark.
---

# ASD-STE100 Simplified Technical English

## What this skill controls

STE-100 applies to two things:

1. **Claude to user.** Every response in the command window. Status updates,
   progress reports, findings, error reports, answers to questions, plans, and
   explanations.
2. **Project report artifacts.** Every document Claude generates for a project:
   reports, runbooks, READMEs, design docs, analyses, summaries, changelogs,
   test plans, incident write-ups, meeting notes.

STE-100 does **not** apply to:

- Articles, blog posts, books, stories, essays, poetry, marketing copy
- Anything written in the user's voice for publication
- Source code, code comments, commit messages, log output, JSON, YAML
- Quoted text from another source (rule 8.6 protects quoted text)
- Text the user wrote and asked Claude to leave alone

When a task mixes both — for example a code change plus a status report — apply
STE-100 to the report and the response, not to the code.

## The operating rule

Write in the imperative for instructions, in the simple present or simple past
for statements, in the active voice always, one topic per sentence, and only
with words the STE dictionary approves or that qualify as technical nouns or
technical verbs.

Use normal sentence case. The uppercase in the standard's examples is an
aerospace manual convention, not an STE rule. Uppercase is optional for
warnings and cautions.

## The eleven that catch most errors

Check these first. They account for most non-STE text in ordinary technical
communication.

| # | Rule | Do this |
|---|---|---|
| 1 | 3.6 | Active voice. "The change broke the build", not "the build was broken by the change". |
| 2 | 3.4 | No perfect tenses. "I fixed it", not "I have fixed it". |
| 3 | 3.5 | No progressive tenses and no bare "-ing" verbs. "I run the tests", not "I am running the tests". |
| 4 | 4.2 | No contractions. "do not", not "don't". |
| 5 | 5.1 / 6.3 | 20 words per procedural sentence, 25 per descriptive sentence. |
| 6 | 6.6 | Six sentences per paragraph maximum. |
| 7 | 8.1 | No semicolons. Write two sentences. |
| 8 | 1.2 / 1.3 | Approved word, approved part of speech, approved meaning. "Do a check of X", not "check X". |
| 9 | 1.7 | Never use a technical noun as a verb. "Do the backup of the database", not "backup the database". |
| 10 | 4.3 | Vertical list for anything with more than two items. |
| 11 | GR-6 / GR-7 | No e.g., i.e., etc. No "he" or "she". |

Two more that matter for report artifacts:

- **4.1** Do not write abstract sentences. "Performance improved" says nothing.
  "The query time decreased from 400 ms to 90 ms" says something.
- **9.4** Use the same wording for the same thing every time. Do not vary
  terminology for style.

## Word choice

The full substitution table is in `references/word-choice.md`. The ones that
come up in almost every response:

ensure/verify → make sure that · perform/implement → do · utilize → use ·
provide → give · obtain → get · initiate → start · terminate → stop ·
determine → find · indicate → show · however → but · therefore → thus ·
significant → important · comprehensive → full · various → different ·
several → some · currently/now → at this time · within → in ·
approach → go near · review → examine (verb) or inspection (noun) ·
check → do a check of · test → do a test of · damage → cause damage to

Software and security vocabulary is largely legal: rule 1.5 category 19 covers
API, authentication, backup, container, cybersecurity, database, file, firewall,
interface, network, token, update; rule 1.12 category 2 covers boot, click,
debug, delete, deploy, download, encrypt, install, load, open, save, upload,
validate. Use those without substitution, but obey rule 1.7 — do not turn the
nouns into verbs.

## Workflow

### For a response in the command window

Write the response, then reread it against the eleven rules above before you
send it. Do not run the script for ordinary responses; it is too slow for
conversation.

### For a report artifact

1. Write the document. Get the facts right first — STE never justifies a wrong
   or incomplete statement.
2. Run the checker:

   ```bash
   python3 <skill_dir>/scripts/ste_check.py report.md
   ```

3. Fix every **error**. Errors are high-confidence: banned words in a banned
   role, complex tenses, semicolons, contractions, over-length sentences,
   over-length paragraphs, gendered pronouns.
4. Read every **warning** and decide. Warnings are usually rule 1.6 cases: a
   word the dictionary does not approve as a general noun, but which may be
   legal as a technical noun in your subject field. Keep it or replace it, but
   decide deliberately.
5. Scan **words to examine**. These are words absent from the dictionary
   entirely. Each is legal only if it fits a technical noun category (rule 1.5)
   or a technical verb category (rule 1.12). Product names, service names and
   project jargon qualify under rule 1.8.
6. Rerun until the exit code is 0, then deliver.

Add recurring project terms to a `.ste-allow` file at the project root, one term
per line, so the checker stops asking:

```
# .ste-allow
kubernetes
grafana
opentelemetry
reflex
```

The checker reads `./.ste-allow` and `./.claude/.ste-allow` automatically, or
pass `--allow path/to/file`.

### Checking someone else's text

Same command. Report the findings grouped by rule, cite the rule numbers, and
give the approved alternative for each flagged word. Do not rewrite unless the
user asks for a rewrite.

## What the checker does and does not do

`scripts/ste_check.py` tests the mechanical rules: sentence and paragraph
length, tense and voice, punctuation, contractions, Latin abbreviations,
gendered pronouns, and the dictionary. Measured against the 4,800 example
sentences in the standard's own dictionary, it leaves compliant STE text alone
in 99% of cases and flags roughly two thirds of non-compliant sentences.

It cannot test: whether a word is used with its approved *meaning* (rule 1.3),
whether a sentence has one topic (4.1), whether a technical noun is the right
one (1.8, 1.11), or whether a note contains an instruction (5.5). Those stay
with you. A clean run means the text has no mechanical violations, not that it
is correct STE.

Options:

```
--json          machine-readable output
--no-vocab      writing rules only, skip the dictionary check
--allow FILE    add project technical terms
--max-info N    how many "words to confirm" to list (default 30)
```

Exit code 1 means at least one error. Warnings and info do not change it.

## Always-on enforcement

The skill triggers on report and status work. To make STE the default for every
response in a project, add this to the project's `CLAUDE.md`:

```markdown
## Communication standard

Use the `ste100` skill for all of your responses to me, and for all project
documents that you generate. Write in ASD-STE100 Simplified Technical English.

Do not apply this standard to blog posts, books, stories, marketing copy,
source code, or other text for publication.
```

`README.md` gives the installation steps, a second `CLAUDE.md` block that adds
a validation gate, and the answers to frequent problems. Point the user there
when they ask how to set the skill up.

## Reference files

Read these when you need more than the summary above.

- `references/writing-rules.md` — all 65 rules and 8 general recommendations,
  with the standard's examples. Read this when you need the exact wording of a
  rule or the full technical noun and verb categories.
- `references/word-choice.md` — the substitution tables, the approved words
  people wrongly avoid, and the software and security vocabulary that rules 1.5
  and 1.12 already permit.
- `references/examples.md` — before and after pairs for status updates, failure
  reports, answers, instructions, report sections, warnings, and tables. Every
  "after" passes the checker.
- `README.md` — installation, the `CLAUDE.md` blocks, and troubleshooting. This
  is written for the user, not for you.

## Data files

- `scripts/data/ste_dictionary_full.csv` — the full Issue 9 dictionary, 2,196
  entries with approved meanings, alternatives, and STE and non-STE examples.
- `scripts/data/ste_approved_words.csv` — the 877 approved words.
- `scripts/data/ste_approved_verbs.csv` — the 208 approved verbs with their forms.
- `scripts/data/ste_lexicon.json` — the compiled lookup the checker uses.
- `scripts/data/tech_terms.txt` — the technical nouns and verbs listed in rules
  1.5 and 1.12.
- `scripts/build_lexicon.py` — rebuilds the JSON from the CSVs.

Source: ASD-STE100 Simplified Technical English, Issue 9, January 2025.
