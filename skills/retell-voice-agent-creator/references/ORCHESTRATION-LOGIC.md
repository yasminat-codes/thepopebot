# Orchestration Logic

Detailed rules governing how the orchestrator chains, dispatches, and manages
context flow between sub-skills.

## Chain Execution Order

The full 8-step chain runs in this exact sequence. No step may be reordered.

```
Step 1: Interview
    |
    v  (interview context object)
Step 2: Voice Selection
    |
    v  (voice_id, voice_provider, voice_name)
Step 3: Prompt Generation
    |
    v  (system_prompt, states[], post_call_analysis_data[])
Step 4: Pronunciation Fixing
    |
    v  (pronunciation_dictionary[], prompt_annotations)
Step 5: Humanization
    |
    v  (humanized_prompt)
Step 6: Latency Optimization
    |
    v  (latency_config)
Step 7: Config Assembly
    |
    v  (llm-config.json, agent-config.json)
Step 8: Deployment
    |
    v  (agent_id, llm_id, deployment_status)
```

## Context Passing Rules

Each step produces output that feeds subsequent steps. The context object
accumulates across all steps.

### Context Object Schema

```json
{
  "interview": {
    "business_name": "",
    "industry": "",
    "use_case": "",
    "agent_name": "",
    "agent_persona": {},
    "voice_preferences": {},
    "conversation_flow_notes": "",
    "pronunciation_terms": [],
    "humanization_level": 5,
    "technical_settings": {},
    "integration_requirements": {},
    "deployment_mode": "internal"
  },
  "voice": {
    "voice_id": "",
    "voice_provider": "",
    "voice_name": ""
  },
  "prompt": {
    "system_prompt": "",
    "states": [],
    "post_call_analysis_data": []
  },
  "pronunciation": {
    "dictionary": [],
    "prompt_annotations": ""
  },
  "humanization": {
    "humanized_prompt": ""
  },
  "latency": {
    "responsiveness": 1,
    "interruption_sensitivity": 0.5,
    "enable_backchannel": true,
    "ambient_sound": "off",
    "end_call_after_silence_ms": 30000,
    "max_call_duration_ms": 1800000
  },
  "config": {
    "llm_config_path": "",
    "agent_config_path": ""
  },
  "deployment": {
    "agent_id": "",
    "llm_id": "",
    "status": ""
  }
}
```

### What Each Step Reads and Writes

| Step | Reads From | Writes To |
|------|-----------|-----------|
| 1. Interview | User input | interview.* |
| 2. Voice Selection | interview.voice_preferences | voice.* |
| 3. Prompt Generation | interview.business_name, industry, use_case, agent_persona, conversation_flow_notes | prompt.* |
| 4. Pronunciation | interview.pronunciation_terms, prompt.system_prompt | pronunciation.* |
| 5. Humanization | prompt.system_prompt, interview.humanization_level | humanization.humanized_prompt |
| 6. Latency | interview.technical_settings, interview.use_case | latency.* |
| 7. Config Assembly | voice.*, humanization.humanized_prompt, pronunciation.dictionary, latency.*, prompt.post_call_analysis_data, prompt.states | config.* |
| 8. Deployment | config.llm_config_path, config.agent_config_path | deployment.* |

## SINGLE Mode Execution

When dispatching to a single sub-skill:

1. Read the sub-skill's SKILL.md in full.
2. Extract the required inputs from the sub-skill's documentation.
3. Validate that you have all required inputs. If not, ask the user.
4. Execute the sub-skill's procedure step by step.
5. Capture the output.
6. If the output is a config change, ask the user if they want to apply it
   to an existing agent (via retell-api-wrapper PATCH).

### Input Validation by Sub-Skill

| Sub-Skill | Required Inputs | Optional Inputs |
|-----------|----------------|-----------------|
| voice-selector | at least one preference (gender, accent, or provider) | warmth, speed, age |
| prompt-generator | business_name, use_case | industry, persona, template_name |
| pronunciation-fixer | word(s) to fix | existing agent_id, voice_provider |
| humanization-engine | system_prompt text | humanization_level, specific elements |
| latency-optimizer | current settings or agent_id | target latency, use_case |
| agent-config-builder | voice_id, system_prompt | all latency/pronunciation configs |
| retell-api-wrapper | API action + required params | agent_id, call_id |

## PARALLEL Mode Execution

Currently used for: latency-optimizer + humanization-engine.

1. Read both sub-skill SKILL.md files.
2. Validate inputs for both sub-skills.
3. Execute both. Since they operate on different config sections (latency
   settings vs prompt text), there are no conflicts.
4. Merge outputs:
   - Latency output goes into the agent config (responsiveness, interruption, etc.)
   - Humanization output replaces the system prompt in the LLM config.
5. Present merged result to user. If applying to existing agent, make two
   API calls: PATCH agent (latency) and PATCH LLM (prompt).

## Error Handling

### Chain Step Failure

If any step in the chain fails:

1. **Save partial output.** Write everything completed so far to the output/
   folder. This prevents losing work.
2. **Report the failure clearly.** State which step failed, what the error was,
   and what was saved.
3. **Offer recovery options:**
   - "Retry this step" — re-execute the failed step.
   - "Skip this step" — continue the chain without this step's output
     (only valid for optional steps: pronunciation, humanization).
   - "Start over" — restart from Step 1.
4. **Mandatory steps that cannot be skipped:** Interview (Step 1), Prompt
   Generation (Step 3), Config Assembly (Step 7), Deployment (Step 8).
5. **Optional steps that can be skipped:** Voice Selection (falls back to
   template default), Pronunciation (skip if no tricky terms), Humanization
   (skip if user wants raw output), Latency (uses template defaults).

### API Failure

If a Retell API call fails:
1. Retry up to 3 times with 2-second delay between retries.
2. On persistent failure, save the config files locally and report:
   "Deployment failed after 3 attempts. Your config has been saved to
   output/. You can deploy manually later with: ./scripts/deploy.sh"

### Input Validation Failure

If a sub-skill's required inputs are missing:
1. Do not proceed with the sub-skill.
2. Ask the user for the specific missing input(s).
3. Resume once provided.

## Fast Chain (Template-Only Deployment)

When the user says "quick deploy" or specifies a template without customization:

1. Skip Interview (Step 1). Use template defaults for all values.
2. Run Voice Selection (Step 2) with template default voice. Confirm with user.
3. Run Prompt Generation (Step 3) with template default prompt.
4. Skip Pronunciation (Step 4). Template prompts avoid tricky words.
5. Skip Humanization (Step 5). Template prompts include built-in humanization.
6. Skip Latency (Step 6). Template defaults are pre-tuned.
7. Run Config Assembly (Step 7).
8. Run Deployment (Step 8).

This reduces the chain to 4 active steps: Voice -> Prompt -> Config -> Deploy.

## Quality Gate Phase (Step 7.5)

The Quality Gate runs between Config Assembly and Deployment. It is NOT optional.

### Gate Checklist

**Prompt Quality:**
- [ ] System prompt under 500 tokens
- [ ] CRITICAL RULES section present (NEVER speak >2 sentences, spell numbers, etc.)
- [ ] NO_RESPONSE_NEEDED instruction present
- [ ] Tool preambles configured for all tools
- [ ] begin_message_delay_ms: 400-500 set
- [ ] enable_dynamic_voice_speed: true set
- [ ] fallback_voice_ids configured

**Pronunciation:**
- [ ] All numbers in knowledge base spelled out in words
- [ ] Email and URL pronunciation rules in prompt
- [ ] Pronunciation dictionary populated for brand names

**Simulation Testing:**
- [ ] Happy Path: ≥95% success rate across 10 simulated calls
- [ ] Objector persona: ≥80% handled without escalation
- [ ] Angry persona: de-escalation in ≥70% of calls

**Gate Decision:**
- All checks pass → Proceed to Deployment (Step 8)
- Any check fails → Return to relevant sub-skill with specific failure details
- Critical failure (prompt quality) → Full rebuild of that section

### Failure Routing

| Failure | Route To |
|---------|----------|
| Prompt too long | prompt-generator |
| Pronunciation errors | pronunciation-fixer |
| Wrong latency settings | latency-optimizer |
| Config validation fails | agent-config-builder |
| Voice sounds wrong | voice-selector |
| Simulation pass rate below threshold | All sub-skills review |
