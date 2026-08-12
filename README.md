# skill_ste100

This repository contains `ste100`, an Agent Skill for Claude. The skill makes
Claude write in ASD-STE100 Simplified Technical English (STE).

STE is a controlled language from the aerospace industry. The standard has 65
rules and a dictionary of approved words. Text in STE is clear, short,
and easy to translate. This skill applies the standard, Issue 9 (January
2025), to the output of Claude.

## What the skill does

The skill controls two types of text:

- Each response that Claude gives you in the command window
- Each project document that Claude writes, for example a report, a runbook,
  or a design document

The skill does not apply to blog posts, books, stories, marketing copy,
source code, or other text for publication.

The skill also contains a checker, `ste_check.py`. The checker does a test of
a document against the mechanical rules of the standard. These rules include
sentence length, paragraph length, tense, voice, punctuation, contractions,
and the dictionary. Claude starts the checker on each document and corrects
the errors before it gives you the document. You can also start the checker
manually on your own documents.

## What is in this repository

| Path | Content |
|---|---|
| `ste100/SKILL.md` | The instructions that Claude reads when the skill starts |
| `ste100/references/writing-rules.md` | All 65 rules and 8 general recommendations |
| `ste100/references/word-choice.md` | The word substitution tables |
| `ste100/references/examples.md` | Text examples before and after correction |
| `ste100/scripts/ste_check.py` | The checker |
| `ste100/scripts/build_lexicon.py` | Makes the lexicon again from the CSV files |
| `ste100/scripts/data/` | The STE dictionary and the compiled lexicon |
| `ste100/README.md` | The full user guide for the skill |

## Deployment

Each method that follows puts the `ste100` directory in a location where
Claude finds skills. Select one method.

### Method 1 — one project

Copy the `ste100` directory into the project:

```bash
git clone https://github.com/rondilley/skill_ste100.git
cp -r skill_ste100/ste100 <project>/.claude/skills/ste100
```

### Method 2 — all projects on one machine

Copy the `ste100` directory into your user directory.

Linux and macOS:

```bash
git clone https://github.com/rondilley/skill_ste100.git
cp -r skill_ste100/ste100 ~/.claude/skills/ste100
```

Windows (PowerShell):

```powershell
git clone https://github.com/rondilley/skill_ste100.git
Copy-Item -Recurse skill_ste100\ste100 $env:USERPROFILE\.claude\skills\ste100
```

### Method 3 — your Claude account

Make a zip archive that contains the `ste100` directory. Give the archive the
name `ste100.skill`. Then upload the archive to the Claude app. The app makes the skill available in all of your sessions, on all
of your machines.

The file `SKILL.md` must be at the first level in the skill directory:

```
ste100/SKILL.md
ste100/references/
ste100/scripts/
```

If the archive has a second directory level, for example
`ste100/ste100/SKILL.md`, the skill does not operate.

### Make sure that the deployment is correct

Start the checker on a test file:

```bash
python3 ~/.claude/skills/ste100/scripts/ste_check.py README.md
```

The checker prints a report and stops with exit code 0 or 1. If the checker
prints an error about the lexicon, the `scripts/data/` directory is not
complete. Copy the directory again.

The checker uses only the Python standard library. Python 3.8 or subsequent
versions are sufficient.

## Turn the skill on for each response

The skill starts automatically for report work and document work. To make STE
the standard for each response, put this block in your `CLAUDE.md`:

```markdown
## Communication standard

Use the `ste100` skill for all of your responses to me, and for all project
documents that you generate. Write in ASD-STE100 Simplified Technical English.

Do not apply this standard to blog posts, books, stories, marketing copy,
source code, or other text for publication.
```

Use `~/.claude/CLAUDE.md` for all of your projects. Use
`<project>/CLAUDE.md` for one project. The user guide at `ste100/README.md`
gives an alternative block with a validation gate, and the answers to
frequent problems.

## Project terminology

Your project has technical nouns that are not in the STE dictionary, for
example product names. Put these terms in a `.ste-allow` file at the root of
the project, one term for each line. The checker reads `./.ste-allow` and
`./.claude/.ste-allow` from the directory where you start it. The user guide
gives the full procedure.

## License

The GNU General Public License, version 3, applies to the code in this
repository. Refer to the `LICENSE` file.

ASD-STE100 is copyright ASD (Aerospace, Security and Defence Industries
Association of Europe) and is a registered trademark of the European Union.
The specification of the standard is available at no cost from
[asd-ste100.org](https://www.asd-ste100.org/).
