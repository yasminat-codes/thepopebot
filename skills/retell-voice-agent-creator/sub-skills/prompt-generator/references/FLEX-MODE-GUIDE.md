# Flex Mode Guide

## What Is Flex Mode

Flex Mode compiles your entire conversation flow into a single structured prompt. Instead of the LLM being locked in a state and only knowing state-specific instructions, it sees the full flow and dynamically navigates based on conversation context.

## When to Use Flex Mode

Use when:
- Conversation path depends heavily on caller input
- Fewer than 20 nodes total
- Caller may need to jump between topics non-linearly
- You want simpler maintenance (one flow vs many state prompts)

Avoid when:
- Compliance requires exact script adherence (debt collection, medical intake)
- More than 20 nodes (hallucination risk increases)
- Per-node Knowledge Base assignment is needed (ignored in Flex Mode)
- Audit trail of exact state transitions is required

## How to Enable

In Retell dashboard: Conversation Flow -> Enable Flex Mode
Or in API: set `"flex_mode": true` on the LLM config.

## Node Types in Flex Mode

- **Conversation Node**: LLM handles dialogue (most nodes)
- **Function Node**: Triggers tool call
- **Logic Node**: Conditional branching
- **End Node**: Terminates call
- **Global Node**: Always accessible from any state

## Limit: 20 Nodes Maximum

Beyond 20 nodes, LLM context overflows and hallucination rates increase. If your flow needs more than 20 nodes, switch to Traditional States.

## Per-Node KB Limitation

In Flex Mode, Knowledge Base assignments at the node level are IGNORED. Assign KB at the agent level only.

## Prompt Structure for Flex Mode

When using Flex Mode, write the general_prompt to describe the FULL conversation arc, not just one phase. Use section headers inside the prompt for each phase. The LLM navigates between sections dynamically.

## Migration: Traditional to Flex Mode

1. Map all existing states and transitions
2. Verify total nodes <= 20
3. Identify any node-level KB assignments (move to agent level)
4. Enable Flex Mode
5. Run 20+ simulation tests before going live
6. Monitor transcript coherence for 48 hours post-launch
