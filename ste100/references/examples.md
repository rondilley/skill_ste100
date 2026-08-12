# Before and after

Every "after" below passes `ste_check.py` with zero errors and zero warnings.

---

## 1. Status update in the command window

**Before**

> I've been working through the authentication refactor and I've now completed
> the token validation piece. There are still a couple of edge cases that need
> to be addressed, e.g. expired refresh tokens, but overall things are looking
> good and I should be able to wrap this up shortly.

**After**

> I did the work on the authentication refactor. The token validation is
> complete. Two conditions are not complete:
>
> - Expired refresh tokens
> - Tokens with an incorrect signature.
>
> I will do this work next.

What changed: perfect tense (3.4), progressive tense (3.5), contractions (4.2),
"e.g." (GR-6), "address" and "complete" as verbs, an abstract sentence
("things are looking good", 4.1), and a vague time ("shortly").

---

## 2. Reporting a failure

**Before**

> Unfortunately the build is currently failing because a dependency was updated
> upstream, which has broken the type signatures in three modules; I'm
> investigating whether we can pin the previous version.

**After**

> The build fails. An upstream change to a dependency caused the failure. The
> change made the type signatures in three modules incorrect. I will examine
> the alternative to pin the previous version.

What changed: progressive (3.5), passive with a known agent (3.6), semicolon
(8.1), contraction (4.2), "investigate" (1.1), one topic per sentence (4.1).

---

## 3. Answering a question

**Before**

> Yeah, you could probably use a bloom filter here — it'd cut your memory
> footprint significantly, though you'd need to handle false positives. Most
> people find it's worth the tradeoff.

**After**

> A bloom filter is possible here. It decreases the memory that the process
> uses. But a bloom filter gives some incorrect results. You must add a second
> check to find these incorrect results.

What changed: contractions (4.2), "significantly" (1.1), "handle" as a verb
(1.1), the phrasal verb "cut ... footprint" (9.3), a vague attribution ("most
people find"), and slang.

---

## 4. Instructions to the user

**Before**

> Before running the migration you'll want to make sure you've taken a backup,
> as the schema changes aren't reversible.

**After**

> Do the backup of the database before you start the migration. The schema
> changes are not reversible.

What changed: procedural writing gets the imperative form (5.3), the condition
comes first (5.4), no contractions (4.2), "backup" stays a technical noun and
does not become a verb (1.7).

---

## 5. A project report section

**Before**

> ## Performance Analysis
>
> Following a comprehensive review of the ingest pipeline, we identified several
> significant bottlenecks that were negatively impacting throughput, the most
> critical of which was an N+1 query pattern in the enrichment stage which was
> being triggered on every record and which accounted for approximately 60% of
> total processing time. Additionally, the batch size had been configured
> sub-optimally.

**After**

> ## Analysis of the performance
>
> We did an inspection of the ingest pipeline. We found three problems that
> decrease the throughput.
>
> The primary problem is in the enrichment step. Each record causes a new
> database query. These queries use approximately 60% of the process time.
>
> The second problem is the number of records in each batch. The configured
> value is too small.

What changed: 62-word sentence (6.3), passive with a known agent (3.6),
progressive (3.5), perfect tense (3.4), "comprehensive", "significant",
"critical", "additionally", "review" (1.1), and one topic per sentence and
per paragraph (4.1, 6.5). "Stage" and "size" are not approved either: use
"step" and "number".

---

## 6. A safety-relevant instruction in a runbook

**Before**

> Warning: don't run this against prod without checking the dry-run output
> first, otherwise you risk deleting live data.

**After**

> WARNING: BEFORE YOU RUN THIS COMMAND AGAINST THE PRODUCTION ENVIRONMENT,
> EXAMINE THE OUTPUT OF THE DRY RUN. IF YOU DO NOT DO THIS, THE COMMAND CAN
> DELETE LIVE DATA.

What changed: rule 7.2 puts the condition first, rule 7.3 adds the consequence,
rule 4.2 removes the contraction, rule 1.10 removes "prod". The uppercase is an
optional house convention, not an STE rule.

---

## 7. Tables

Table cells obey the same rules. Keep each cell to one clause.

**Before**

| Finding | Status |
|---|---|
| The certificate rotation job has been failing intermittently since June | Being investigated |

**After**

| Problem | Condition |
|---|---|
| The certificate rotation task fails. The failures started in June. | Investigation in progress |

---

## What STE will not fix

STE controls the words and the grammar. It does not make a wrong statement
right. A short, clear, active sentence that reports the wrong number is still
wrong. Accuracy comes first, then STE.

STE also does not require you to remove information. If a sentence needs 40
words of content, write two sentences of 20, not one sentence of 20 that leaves
half the facts out. Rule 4.2 is explicit: do not omit words to make sentences
shorter.
