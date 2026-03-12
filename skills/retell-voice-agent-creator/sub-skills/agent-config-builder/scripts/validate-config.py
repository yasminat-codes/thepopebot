#!/usr/bin/env python3
"""
validate-config.py — Validate llm-config.json and agent-config.json against
Retell AI API schema.

Usage:
    python3 validate-config.py --llm-config llm-config.json --agent-config agent-config.json
"""

import argparse
import json
import sys


class ConfigValidator:
    def __init__(self):
        self.results = []  # (status, config, message)

    def _add(self, status, config, message):
        self.results.append((status, config, message))

    def check_required(self, config, config_name, field):
        if field in config and config[field]:
            self._add("PASS", config_name, f"{field} is present")
        else:
            self._add("FAIL", config_name, f"{field} is required but missing")

    def check_range(self, config, config_name, field, min_val, max_val):
        if field not in config:
            return
        val = config[field]
        if not isinstance(val, (int, float)):
            self._add("FAIL", config_name, f"{field} must be a number, got {type(val).__name__}")
            return
        if min_val <= val <= max_val:
            self._add("PASS", config_name, f"{field} ({val}) is in range [{min_val}, {max_val}]")
        else:
            self._add("FAIL", config_name, f"{field} ({val}) is out of range [{min_val}, {max_val}]")

    def check_enum(self, config, config_name, field, allowed):
        if field not in config:
            return
        val = config[field]
        if val in allowed:
            self._add("PASS", config_name, f"{field} ('{val}') is valid")
        else:
            self._add("FAIL", config_name, f"{field} ('{val}') must be one of: {', '.join(allowed)}")

    def check_type_array(self, config, config_name, field):
        if field not in config:
            return
        if isinstance(config[field], list):
            self._add("PASS", config_name, f"{field} is an array")
        else:
            self._add("FAIL", config_name, f"{field} must be an array, got {type(config[field]).__name__}")

    def check_type_bool(self, config, config_name, field):
        if field not in config:
            return
        if isinstance(config[field], bool):
            self._add("PASS", config_name, f"{field} is boolean")
        else:
            self._add("FAIL", config_name, f"{field} must be boolean, got {type(config[field]).__name__}")

    def check_pronunciation_entries(self, config, config_name):
        if "pronunciation_dictionary" not in config:
            return
        entries = config["pronunciation_dictionary"]
        if not isinstance(entries, list):
            self._add("FAIL", config_name, "pronunciation_dictionary must be an array")
            return
        for i, entry in enumerate(entries):
            for req_field in ["word", "alphabet", "phoneme"]:
                if req_field not in entry or not entry[req_field]:
                    self._add("FAIL", config_name,
                              f"pronunciation_dictionary[{i}] missing '{req_field}'")

    def check_analysis_entries(self, config, config_name):
        if "post_call_analysis_data" not in config:
            return
        entries = config["post_call_analysis_data"]
        if not isinstance(entries, list):
            self._add("FAIL", config_name, "post_call_analysis_data must be an array")
            return
        valid_types = {"string", "boolean", "number", "enum"}
        for i, entry in enumerate(entries):
            for req_field in ["name", "type", "description"]:
                if req_field not in entry or not entry[req_field]:
                    self._add("FAIL", config_name,
                              f"post_call_analysis_data[{i}] missing '{req_field}'")
            if "type" in entry and entry["type"] not in valid_types:
                self._add("FAIL", config_name,
                          f"post_call_analysis_data[{i}] type '{entry['type']}' invalid")

    def check_state_edges(self, config, config_name):
        if "states" not in config:
            return
        states = config["states"]
        if not isinstance(states, list):
            return
        state_names = {s.get("name") for s in states if "name" in s}
        for state in states:
            for edge in state.get("edges", []):
                dest = edge.get("destination_state_name", "")
                if dest not in state_names:
                    self._add("FAIL", config_name,
                              f"state '{state.get('name')}' edge references unknown state '{dest}'")

    def check_cross_config_warnings(self, llm_config, agent_config):
        if llm_config.get("states") and llm_config.get("general_prompt"):
            self._add("WARN", "llm", "states defined — general_prompt may be ignored by Retell")
        if llm_config.get("start_speaker") == "user" and llm_config.get("begin_message"):
            self._add("WARN", "llm", "start_speaker is 'user' — begin_message will be ignored")
        if agent_config.get("enable_backchannel") is False:
            if agent_config.get("backchannel_frequency") or agent_config.get("backchannel_words"):
                self._add("WARN", "agent",
                          "enable_backchannel is false — backchannel settings will be ignored")
        if "ambient_sound" not in agent_config and "ambient_sound_volume" in agent_config:
            self._add("WARN", "agent",
                      "ambient_sound_volume set but ambient_sound not specified")

    def validate(self, llm_config, agent_config):
        # LLM required fields
        self.check_required(llm_config, "llm", "start_speaker")
        self.check_enum(llm_config, "llm", "start_speaker", ["agent", "user"])

        # LLM ranges
        self.check_range(llm_config, "llm", "model_temperature", 0, 2)

        # LLM types
        self.check_type_array(llm_config, "llm", "states")
        self.check_type_array(llm_config, "llm", "general_tools")
        self.check_type_array(llm_config, "llm", "knowledge_base_ids")

        # LLM state edges
        self.check_state_edges(llm_config, "llm")

        # Agent required fields
        self.check_required(agent_config, "agent", "voice_id")

        # Agent ranges
        self.check_range(agent_config, "agent", "voice_temperature", 0, 2)
        self.check_range(agent_config, "agent", "voice_speed", 0.5, 2)
        self.check_range(agent_config, "agent", "volume", 0, 2)
        self.check_range(agent_config, "agent", "responsiveness", 0, 1)
        self.check_range(agent_config, "agent", "interruption_sensitivity", 0, 1)
        self.check_range(agent_config, "agent", "backchannel_frequency", 0, 1)
        self.check_range(agent_config, "agent", "ambient_sound_volume", 0, 2)
        self.check_range(agent_config, "agent", "end_call_after_silence_ms", 1000, 600000)
        self.check_range(agent_config, "agent", "max_call_duration_ms", 60000, 7200000)

        # Agent enums
        self.check_enum(agent_config, "agent", "voice_emotion",
                        ["calm", "sympathetic", "happy", "sad", "angry", "fearful", "surprised"])
        self.check_enum(agent_config, "agent", "ambient_sound",
                        ["coffee-shop", "convention-hall", "summer-outdoor",
                         "mountain-outdoor", "static-noise", "call-center"])
        self.check_enum(agent_config, "agent", "denoising_mode",
                        ["no-denoise", "noise-cancellation",
                         "noise-and-background-speech-cancellation"])
        self.check_enum(agent_config, "agent", "data_storage_setting",
                        ["everything", "everything_except_pii", "basic_attributes_only"])

        # Agent types
        self.check_type_array(agent_config, "agent", "fallback_voice_ids")
        self.check_type_array(agent_config, "agent", "backchannel_words")
        self.check_type_array(agent_config, "agent", "pronunciation_dictionary")
        self.check_type_array(agent_config, "agent", "post_call_analysis_data")
        self.check_type_array(agent_config, "agent", "webhook_events")
        self.check_type_array(agent_config, "agent", "boosted_keywords")
        self.check_type_bool(agent_config, "agent", "enable_backchannel")
        self.check_type_bool(agent_config, "agent", "enable_dynamic_voice_speed")
        self.check_type_bool(agent_config, "agent", "normalize_for_speech")

        # Structural checks
        self.check_pronunciation_entries(agent_config, "agent")
        self.check_analysis_entries(agent_config, "agent")

        # Cross-config warnings
        self.check_cross_config_warnings(llm_config, agent_config)

    def report(self):
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for status, config_name, message in self.results:
            counts[status] = counts.get(status, 0) + 1
            print(f"{status:4s}  [{config_name}]  {message}")

        print("---")
        print(f"Results: {counts['PASS']} PASS, {counts['WARN']} WARN, {counts['FAIL']} FAIL")
        return counts["FAIL"] == 0


def main():
    parser = argparse.ArgumentParser(description="Validate Retell config files.")
    parser.add_argument("--llm-config", required=True, help="Path to llm-config.json")
    parser.add_argument("--agent-config", required=True, help="Path to agent-config.json")
    args = parser.parse_args()

    try:
        with open(args.llm_config, "r") as f:
            llm_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {args.llm_config}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.agent_config, "r") as f:
            agent_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {args.agent_config}: {e}", file=sys.stderr)
        sys.exit(1)

    validator = ConfigValidator()
    validator.validate(llm_config, agent_config)
    passed = validator.report()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
