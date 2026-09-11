# JSONL Check

A small, local JSON Lines validator for inspecting AI datasets and application logs. Python 3.10+; no third-party packages or network requests.

This is an original AI-assisted portfolio project, not a paid client case study. It does not demonstrate or claim earnings.

## Run

```sh
python jsonl_check.py your-data.jsonl
python jsonl_check.py your-data.jsonl --objects-only --max-errors 10
python jsonl_check.py demo.jsonl
python -m unittest -v
```

The demo intentionally contains one syntax error and one blank line. It should report five lines, three valid records, and two errors. Its exit code is 1 because the demo contains errors.

Reports contain line numbers, error categories, and counts. They do not include input filenames or record text. The source file is never modified. All processing happens on your machine.

Exit codes: **0** = all checked records valid; **1** = invalid or uncheckable records; **2** = input cannot be read or arguments are invalid.

## What is checked

- UTF-8 encoding, without a byte order mark.
- One valid JSON value on each line; blank lines are rejected.
- NaN and Infinity literals are rejected.
- CRLF and a final record without a trailing newline are accepted.
- Optional object-only mode for datasets that require object records.
- Error output is capped, while every input line is still counted.

The behavior follows the [JSON Lines format](https://jsonlines.org/). Empty input contains zero records and passes format checking. This does not imply that the dataset is suitable for training: schema, content rights, personal data, duplicate records and model-specific requirements are outside this tool's scope. Duplicate JSON object keys are accepted. Extremely deep records may exceed Python's parser limit and are reported as uncheckable. Processing keeps one physical line and its parsed value in memory, so memory depends on the largest record.

## Request a small paid adaptation

An introductory **US$5 fixed-price offer** is available for one agreed validation rule in this tool. For example: require each object to contain a non-empty `prompt` string. The delivery includes the patch, regression tests, running instructions, and one revision within the same agreed scope. AI assistance is used, and the relevant tests are run.

Open an [issue](https://github.com/tiangongyi905-ai/jsonl-check/issues) with a synthetic example, the expected output, and your Python version. Feasibility, the exact acceptance criteria, and delivery time must be agreed before a paid task is accepted. Larger changes need a separate quote. The existing open-source tool remains free under its MIT license.

Payment for an agreed adaptation can be arranged through PayPal using an appropriate private payment channel; never post payment details in an issue. This offer does not include hosting, access to production systems, or guarantees about AI training results. Do not post real datasets, passwords, API keys, personal information, or private code. Public issues are suitable only for public or synthetic examples.
