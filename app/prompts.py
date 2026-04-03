
DIAGNOSIS_PROMPT = """\
You are an expert software engineer diagnosing a test failure.

## Validation Command
{validation_command}

## Attempt
{attempt_count} of {max_retries}

## Failure Output
{output}

## Suspected Files
{suspected_files}

## Instructions
- Identify the root cause of the failure in one sentence.
- List the specific file(s) and line(s) most likely responsible.
- Do not suggest a fix yet.
- Do not include irrelevant files or speculation.

## Output Format
Root Cause: <one sentence>
Responsible Files: <comma-separated list>
"""




PATCH_PROMPT = """\
You are an expert software engineer fixing a failing test.

## Failure Summary
{failure_summary}

## File To Fix
{file_name}

## Current File Content
{file_content}

## Instructions
- Fix only the code that caused the failure.
- Do not rename, refactor, or rewrite unrelated code.
- Do not add comments, docstrings, or imports unless required by the fix.
- Return the complete corrected file content only.
- Do not include explanations, markdown, or code fences.
"""
