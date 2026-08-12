# Word choice: the substitutions that do the most work

Every replacement below comes from the ASD-STE100 Issue 9 dictionary. The full
list is `scripts/data/ste_dictionary_full.csv` (2,196 entries: 877 approved
words, 1,319 not approved with their approved alternatives).

Look a word up directly:

```bash
python3 -c "
import json,sys
d=json.load(open('scripts/data/ste_lexicon.json'))
w=sys.argv[1].lower()
print('APPROVED as', d['approved'][w]) if w in d['approved'] else None
print('NOT APPROVED:', d['not_approved'].get(w))
" utilize
```

---

## Verbs that appear constantly in status and report writing

| Not approved | Use |
|---|---|
| ensure, verify, confirm | make sure (that) |
| perform, implement, execute, conduct | do |
| utilize, employ, adopt | use |
| provide, deliver | give, supply |
| obtain, acquire | get |
| initiate, begin, commence | start |
| terminate, cease | stop |
| proceed | continue |
| determine | find, calculate, select |
| indicate | show, identify |
| assess, evaluate | examine, calculate |
| analyze | do the analysis of |
| investigate | do the investigation of |
| review (v) | examine |
| create, produce, generate | make, cause, supply |
| construct | assemble |
| develop | start, cause |
| facilitate, assist | help |
| enable, allow, permit | let |
| require, need | be necessary |
| attempt | try |
| happen, arise | occur |
| reduce | decrease |
| improve | make better |
| affect, impact | have an effect on |
| assume | think |
| appear (to be) | seem is not approved — use "show", "think", or "possible" |
| handle | move, touch, use |
| fix | attach, set, repair, install |
| check (v) | do a check of, make sure that, examine |
| test (v) | do a test of |
| damage (v) | cause damage to |
| work (v) | do work |
| detect | find (unless it is a technical verb in context) |
| resolve | repair, correct, make correct |
| identify (v) | identify **is** approved — keep it |

## Adjectives and adverbs

| Not approved | Use |
|---|---|
| comprehensive, entire, whole | full, all |
| significant, critical | important, very important |
| vital, essential | mandatory |
| major | primary |
| minor | small |
| various | different |
| several | some |
| few | a small number of |
| specific | specified, approved |
| normal | usual, correct |
| extremely, highly | very |
| rapidly | quickly |
| eventually | after some time |
| now | at this time |
| currently | at this time |
| later | subsequent, then, after |
| approximately | approximately **is** approved — keep it |

## Connectives and prepositions

| Not approved | Use |
|---|---|
| however | but |
| therefore, consequently | thus, as a result |
| moreover, furthermore, additionally | and, also |
| within | in, in less than |
| under (as "less than") | below (position), less than (limit) |
| over (as "more than") | above (position), more than (limit) |
| prior to | before |
| e.g. | for example |
| i.e. | that is |
| etc. | and so on |

## Nouns

| Not approved | Use |
|---|---|
| finding | result |
| technique | method |
| review (n) | inspection |
| detail (n) | instruction |
| issue | problem (or keep as a technical noun where it means a document issue) |
| concern | problem |
| support (n) | support **is** permitted as a technical noun |

---

## Words STE approves that people wrongly avoid

These are all approved. Prefer them.

**Verbs:** absorb, accept, add, adjust, apply, approve, assemble, attach,
be, become, calculate, cause, change, clean, close, connect, continue,
correct, decrease, discard, disconnect, do, examine, extend, find, get, give,
go, have, help, hold, identify, increase, install, keep, let, lubricate, make,
make sure, measure, monitor, move, obey, occur, open, operate, prevent, push,
put, read, refer, release, remove, repair, replace, report, see, select, send,
set, show, start, stop, supply, tell, think, touch, try, turn, use, wait.

**Nouns:** access, accident, adjustment, aid, analysis, approval, area, check,
condition, damage, data, difference, direction, distance, effect, end, error,
example, failure (technical noun), function, help (verb only — use "aid" as the
noun), inspection, instruction, investigation, item, level, limit, method,
number, part, position, pressure, problem, procedure, process, quantity,
reason, record, report, requirement, result, risk, sequence, side, sign,
surface, task, temperature, test, time, tool, type, unit, value, view, work.

**Adjectives:** able, accurate, applicable, approved, available, careful,
clean, clear, correct, dangerous, different, difficult, dry, easy, empty, equal,
full, high, important, incorrect, large, last, long, low, mandatory, maximum,
minimum, necessary, new, normal (not approved — use "usual"), old, permitted,
possible, primary, ready, related, safe, same, short, similar, small, specified,
strong, sufficient, thin, usual, wet.

---

## Technical nouns and technical verbs in software and security work

Rule 1.5 category 19 and rule 1.12 category 2 make most of this vocabulary
legal. These are permitted without substitution:

**Nouns:** AI, API, artificial intelligence, authentication, backup, backup
file, chatbot, container, content, cybersecurity, database, deep learning,
e-mail, embedding, field, file, firewall, HTML, icon, interface, internet,
laptop, large language model, machine learning, memory, metadata, network,
operating system, plug-in, pre-loaded software, preset value, prompt
engineering, screen, search engine, smartphone, status bar, store, tablet,
token, toolbar, touchscreen, tuning, update, XML.

**Verbs:** abort, boot, clear, click, close, copy, cut, debug, delete,
deselect, digitize, disable, download, drag, enable, encrypt, enter, erase,
filter, format, highlight, install, invalidate, load, manage, maximize,
minimize, navigate, open, paste, print, process, reboot, save, scroll, sort,
store, swipe, tap, type, update, upgrade, upload, validate, zoom.

Two constraints still apply:

1. **Rule 1.7 — do not use a technical noun as a verb.** "Backup the database"
   is wrong; "Do the backup of the database" is right. Same for "email the
   report" → "send the report by e-mail."
2. **Rule 1.12 — do not reach for a technical verb when an approved verb
   works.** "Detect the error" → "Find the error." Keep "detect" for a sensor
   or a scanner that genuinely detects.

Project-specific terms (product names, service names, internal jargon that has a
real definition) are technical nouns under rules 1.5 and 1.8. Put them in a
`.ste-allow` file at the project root, one per line, so the checker stops asking
about them.
