# ste100

The `ste100` skill makes Claude write in ASD-STE100 Simplified Technical
English (STE). The skill applies to two things:

- Each response that Claude gives you in the command window
- Each project document that Claude writes

The skill does not apply to blog posts, books, stories, marketing copy, or
other text for publication.

This README tells you how to install the skill. It also tells you how to add
the skill to `CLAUDE.md` so that Claude uses the skill in each session.

---

## 1. Install the skill

The package is `ste100.skill`. The package is a standard zip archive. Select
one of the three methods that follow.

### Method 1 — one project

Extract the package into the project:

```
<project>/.claude/skills/ste100/
```

The result must look like this:

```
<project>/.claude/skills/ste100/SKILL.md
<project>/.claude/skills/ste100/references/
<project>/.claude/skills/ste100/scripts/
```

### Method 2 — all projects on this machine

Extract the package into your user directory:

- Linux and macOS: `~/.claude/skills/ste100/`
- Windows: `%USERPROFILE%\.claude\skills\ste100\`

### Method 3 — your Claude account

Upload `ste100.skill` in the Claude app. The app then makes the skill
available to all of your sessions, on all of your machines.

### Make sure that the installation is correct

Start the checker on a test file:

```bash
python3 ~/.claude/skills/ste100/scripts/ste_check.py README.md
```

The checker prints a report. If the checker prints an error about the lexicon,
the data directory is not complete. Extract the package again.

---

## 2. Add the skill to CLAUDE.md

The skill has a description. Claude reads the description and selects the skill
for report work and for document work. But a description is not an
instruction. To make STE the standard for each response, put an instruction in
`CLAUDE.md`.

`CLAUDE.md` is the file that Claude reads at the start of each session. Claude
reads these files in this sequence:

| File | Scope |
|---|---|
| `~/.claude/CLAUDE.md` | All projects for this user |
| `<project>/CLAUDE.md` | One project |
| `<project>/<subdirectory>/CLAUDE.md` | One subdirectory |

A `CLAUDE.md` in a project replaces a `CLAUDE.md` in your user directory. If
you want STE in all of your work, use `~/.claude/CLAUDE.md`. If you want STE in
one project only, use the `CLAUDE.md` of that project.

### The standard block

Copy this text into `CLAUDE.md`:

```markdown
## Communication standard

Use the `ste100` skill for all of your responses to me, and for all project
documents that you generate. Write in ASD-STE100 Simplified Technical English.

Do not apply this standard to blog posts, books, stories, marketing copy,
source code, or other text for publication.
```

### The block with a validation gate

Use this alternative if Claude must start the checker before it gives you the
document:

```markdown
## Communication standard

Use the `ste100` skill for all of your responses to me, and for all project
documents that you generate. Write in ASD-STE100 Simplified Technical English.

Before you give me a report, a README, a runbook, or a design document, start
the checker:

    python3 ~/.claude/skills/ste100/scripts/ste_check.py <file>

Correct each error. Make a decision about each warning. Do not deliver the
document until the exit code is 0.

Do not apply this standard to blog posts, books, stories, marketing copy,
source code, or other text for publication.
```

The path in the block must agree with your installation method. For a
project installation, the path is
`.claude/skills/ste100/scripts/ste_check.py`.

### Where to put the block

Put the block near the top of `CLAUDE.md`, after the title. Instructions at the
top of the file get more attention than instructions at the bottom.

---

## 3. Make sure that the skill operates

Start a new session in the project. Then tell Claude:

> What communication standard do you use in this project?

Two conditions show you that the setup is correct:

- Claude tells you about ASD-STE100 and about the `ste100` skill
- The response of Claude is in STE. There are no contractions, no semicolons,
  and no passive voice.

You can also start the skill manually with `/ste100`.

---

## 4. Project terminology

The dictionary of the standard has 877 approved words. Your project has many
technical nouns that are not in the dictionary. Rules 1.5, 1.6 and 1.8 let you
use these technical nouns.

Put your project terminology in a `.ste-allow` file at the root of the project:

```
# .ste-allow
kubernetes
grafana
opentelemetry
terraform
```

The checker reads `./.ste-allow` and `./.claude/.ste-allow` automatically. You
can also give a different file with `--allow <file>`.

---

## 5. The checker

```bash
python3 scripts/ste_check.py report.md
```

The checker gives three levels of result:

| Level | Meaning | Action |
|---|---|---|
| Error | A mechanical violation of a rule | Correct it |
| Warning | A word that can be a technical noun (rule 1.6) | Make a decision |
| Word to examine | A word that is not in the dictionary | Keep it only as a technical noun or a technical verb |

The exit code is 1 if there is one error or more. Warnings do not change the
exit code.

Alternatives:

- `--json` gives machine-readable output
- `--no-vocab` tests the grammar rules only, and not the dictionary
- `--allow <file>` adds your project terminology
- `--max-info <n>` sets the number of words to examine in the report

### The limits of the checker

The checker tests the mechanical rules. These are sentence length, paragraph
length, tense, voice, punctuation, contractions, Latin abbreviations, gendered
pronouns, and the dictionary.

The checker cannot test four important rules:

- The approved meaning of a word (rule 1.3)
- One topic in each sentence (rule 4.1)
- The correct selection of a technical noun (rules 1.8 and 1.11)
- The correct use of notes (rule 5.5).

You must do these four tests.

An exit code of 0 tells you that the text has no mechanical violation. It does
not tell you that the text is correct STE.

---

## 6. What is in the package

| File | Content |
|---|---|
| `SKILL.md` | The skill. The scope, the primary rules, and the workflow |
| `references/writing-rules.md` | All 65 rules and 8 general recommendations |
| `references/word-choice.md` | The substitution tables and the approved words |
| `references/examples.md` | Examples before and after correction |
| `scripts/ste_check.py` | The checker |
| `scripts/build_lexicon.py` | Makes the lexicon again from the dictionary |
| `scripts/data/ste_dictionary_full.csv` | The full dictionary, 2196 entries |
| `scripts/data/ste_approved_words.csv` | The 877 approved words |
| `scripts/data/ste_approved_verbs.csv` | The 208 approved verbs with the approved form of each |
| `scripts/data/ste_lexicon.json` | The compiled lookup for the checker |
| `scripts/data/tech_terms.txt` | The technical nouns and verbs of rules 1.5 and 1.12 |

---

## 7. Frequent problems

**Claude does not use the skill.** Make sure that `SKILL.md` is at
`<skill directory>/SKILL.md`, and not at `<skill directory>/ste100/SKILL.md`.
If there is a second level of directory, the skill does not operate.

**The checker gives many words to examine.** This is correct for the first
inspection of a document. Put your project terminology in `.ste-allow`. The
number then becomes small.

**The checker gives an error for a correct technical noun.** Add the word to
`.ste-allow`. Rule 1.8 lets you use the technical nouns of your
company, industry, or subject field.

**Claude writes in STE in a blog post.** The instruction in `CLAUDE.md` must
have the exclusion sentence. Tell Claude that the text is for publication.

---

Source: ASD-STE100 Simplified Technical English, Issue 9, January 2025.
ASD-STE100 is copyright ASD (Aerospace, Security and Defence Industries
Association of Europe) and is a registered trademark of the European Union.
