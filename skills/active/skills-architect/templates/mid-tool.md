---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}}
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This skill focuses on a single well-defined task using a small set of tools. It follows a
linear execution model: gather input, run the core operation, validate output, present results.

**Tools used:**
{{TOOLS}}

**Typical runtime:** under 60 seconds

---

## Inputs

Before starting, identify what is needed:

| Input | Source | Required |
|-------|--------|----------|
| Primary input | User prompt or current file | Yes |
| Configuration | Inline defaults or user-supplied | No |
| Context | Current working directory | Auto |

---

## Phase 1: Input Collection

Read and validate the primary input.

```
Action: Read the user's request carefully. Extract:
- The target (file, text, identifier, etc.)
- Any explicit options or preferences
- The desired output format
```

**If input is ambiguous:**
Ask one clarifying question before proceeding. Do not make assumptions about intent.

**Validation checklist:**
- [ ] Primary input is present and non-empty
- [ ] Input format matches what the tool expects
- [ ] No conflicting options detected

---

## Phase 2: Core Operation

Execute the primary tool operation.

{{PHASES}}

### Standard Execution

```
1. Prepare the input in the format required by {{TOOLS}}
2. Execute the tool call with validated parameters
3. Capture the raw output
4. Check for errors in the response
```

### Error Handling

If the tool returns an error:

| Error Type | Recovery Action |
|------------|-----------------|
| Invalid input | Re-prompt user with specific correction needed |
| Tool unavailable | Explain limitation, offer manual alternative |
| Timeout | Retry once, then surface partial result |
| Empty result | Confirm input was valid, report no results found |

---

## Phase 3: Output Formatting

Transform the raw tool output into a clean, usable result.

### Output Standards

- Use markdown formatting for structured data
- Include the key result at the top (no preamble)
- Add explanation only when the result is non-obvious
- Provide copy-ready blocks for any code or commands

### Output Template

```
## Result

[PRIMARY OUTPUT HERE]

## Details

[SUPPORTING DETAILS IF NEEDED]

## Next Steps

[OPTIONAL: WHAT TO DO WITH THIS RESULT]
```

---

## Phase 4: Validation

Before presenting results, verify:

{{QUALITY_GATES}}

| Gate | Check | Pass Condition |
|------|-------|----------------|
| Completeness | All parts of the request addressed | No gaps |
| Accuracy | Output matches input intent | Semantically correct |
| Format | Output is properly formatted | Renders cleanly |
| Actionability | User can immediately use the result | No extra steps needed |

---

## Reference Patterns

{{REFERENCES}}

### Pattern: Standard Tool Call

```python
# Example structure — adapt to the actual tool
result = tool_name(
    input=validated_input,
    option_a=default_or_user_value,
    option_b=default_or_user_value,
)
```

### Pattern: Result Validation

```python
if not result or result.get("error"):
    # Surface the error clearly
    return f"Could not complete: {result.get('error', 'unknown error')}"
```

### Pattern: Output Formatting

```markdown
## {{SKILL_NAME}} Result

**Input:** `{original_input}`
**Generated:** {timestamp}

---

{formatted_output}
```

---

## Defaults and Configuration

When the user does not specify options, use these defaults:

| Option | Default | Reason |
|--------|---------|--------|
| Output format | Markdown | Most universally useful |
| Verbosity | Medium | Balanced detail |
| Encoding | UTF-8 | Universal compatibility |

---

## Limitations

- This skill handles one item at a time. For bulk operations, invoke it in a loop.
- Maximum input size: determined by tool limits.
- Does not persist results — copy output before continuing.

---

## Examples

### Example 1: Basic Usage

**Input:** "{{SKILL_NAME}} — process this: [sample input]"

**Output:**
```
[Sample formatted output demonstrating the skill's core function]
```

### Example 2: With Options

**Input:** "{{SKILL_NAME}} — process [input] with [specific option]"

**Output:**
```
[Sample output showing how options affect the result]
```

---

*Tier 2 skill — single tool focus, linear execution. For multi-tool workflows, see advanced-multi-tool template.*
