"""
ecoSential AI-Pro — Autonomous Agent Core (Groq Integrated)
"""

import os
import json
import re
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from groq import Groq

from backend.memory import MemorySystem
from backend.learning import PatternDetector, calculate_reward
from backend.tools import (
    adjust_cooling_system, adjust_power_level, adjust_rpm,
    schedule_maintenance, trigger_alert, calculate_energy_efficiency, predict_failure_window
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SYSTEM_PROMPT = """
You are ecoSential AI-Pro — an elite autonomous industrial intelligence agent.
Your mission: Protect machines, optimize energy, prevent failures, and save lives.

You operate in a smart factory and analyze real-time sensor data to make precise decisions.
You have access to the following tools:
  1. adjust_cooling_system(cooling_rate: 0-100%)
  2. adjust_power_level(power_pct: 20-100%)
  3. adjust_rpm(target_rpm: number)
  4. schedule_maintenance(priority: URGENT|HIGH|ROUTINE, reason: str)
  5. trigger_alert(severity: CRITICAL|WARNING|INFO, title, details)
  6. monitor_only — no action, continue observation

Decision Guidelines:
  - temperature > 100°C OR vibration > 8 mm/s → CRITICAL response required
  - temperature 88-100°C OR vibration 5.5-8 → WARNING, intervene proactively
  - temperature < 88°C AND vibration < 5.5 → NORMAL, monitor or optimize

IMPORTANT: You MUST respond ONLY in valid JSON. No prose outside the JSON block.

JSON Schema:
{
  "chain_of_thought": "Step-by-step reasoning process here",
  "risk_assessment": "One sentence risk summary",
  "action_type": "alert|adjust_params|maintenance|monitor",
  "tools_to_call": [
    {
      "tool": "tool_name",
      "params": { "param1": "value" }
    }
  ],
  "explanation": "Human-readable plain-English explanation of the decision",
  "confidence": 0.95,
  "expected_outcome": "What you expect to happen after this action"
}
"""

class AutonomousAgent:
    def __init__(self):
        self.memory = MemorySystem(persist_dir="./memory_store")
        self.learning = PatternDetector()
        self.cycle_counts: dict[str, int] = {}
        self.total_cycles = 0

        self.client = None
        if GROQ_API_KEY:
            try:
                self.client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"[Agent] Groq init error: {e}")

    def run_cycle(self, machine_id: str, sensor_data: dict) -> dict:
        self.total_cycles += 1
        self.cycle_counts[machine_id] = self.cycle_counts.get(machine_id, 0) + 1

        observation_summary = (
            f"Machine {machine_id}: Temp={sensor_data['temperature']}°C, "
            f"Vib={sensor_data['vibration']} mm/s, Energy={sensor_data['energy_consumption']} kW, "
            f"Health={sensor_data['health_score']}%, Status={sensor_data['status']}"
        )

        relevant_memories = self.memory.retrieve_relevant(observation_summary, top_k=3)
        session_context = self.memory.get_short_term_summary(last_n=3)

        energy_report = calculate_energy_efficiency(machine_id, sensor_data["energy_consumption"])
        failure_pred = predict_failure_window(machine_id, sensor_data["vibration"], sensor_data["temperature"], sensor_data["health_score"])

        decision = self._reason(sensor_data, observation_summary, relevant_memories, session_context, energy_report, failure_pred)
        tool_results = self._execute_tools(machine_id, decision, sensor_data)

        before_health = sensor_data["health_score"]
        after_health_est = min(100, before_health + (5 if decision.get("action_type") != "monitor" else 0))

        reward, reward_rationale = calculate_reward(
            sensor_data=sensor_data, action_type=decision.get("action_type", "monitor"),
            action_result=tool_results[0] if tool_results else {"success": True},
            before_health=before_health, after_health_estimate=after_health_est,
        )

        self.learning.record(machine_id, decision.get("action_type", "monitor"), reward)

        self.memory.add_memory(
            machine_id=machine_id, event_type="action", context=observation_summary,
            decision=f"{decision.get('action_type')}: {decision.get('explanation', '')[:200]}",
            outcome="; ".join([r.get("message", "") for r in tool_results]),
            reward=reward, tags=[sensor_data["status"], decision.get("action_type", "monitor")],
        )

        return {
            "cycle_id": self.total_cycles, "machine_id": machine_id, "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data, "observation_summary": observation_summary,
            "energy_report": energy_report, "failure_prediction": failure_pred,
            "relevant_memories": relevant_memories, "decision": decision,
            "tool_results": tool_results, "reward": reward, "reward_rationale": reward_rationale,
            "learning_insights": self.learning.get_insights(), "memory_stats": self.memory.get_stats(),
        }

    def _reason(self, sensor_data, observation_summary, relevant_memories, session_context, energy_report, failure_pred) -> dict:
        memories_text = "\n".join([f"  • [{m.get('timestamp','')[:10]}] {m.get('context','')[:80]} → Action: {m.get('decision','')[:60]} | Reward: {m.get('reward', 0):+.1f}" for m in relevant_memories]) or "  No relevant past memories yet."

        prompt = f"""
## Current Machine State
{json.dumps(sensor_data, indent=2)}

## Energy Analysis
Efficiency Index: {energy_report.get('efficiency_index', 'N/A')}

## Failure Prediction
Estimated Time-to-Failure: {failure_pred.get('estimated_ttf_hours', 'N/A')} hours

## Relevant Past Experiences
{memories_text}

Analyze the current state and determine the best action. Output strictly valid JSON.
"""
        if self.client and GROQ_API_KEY:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-70b-8192", # Groq's insanely fast and smart LLaMA 3
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                raw = chat_completion.choices[0].message.content.strip()
                return json.loads(raw)
            except Exception as e:
                print(f"[Agent] Groq LLM error: {e}")

        return self._rule_based_fallback(sensor_data)

    def _rule_based_fallback(self, sensor_data: dict) -> dict:
        status = sensor_data.get("status", "NORMAL")
        temp = sensor_data.get("temperature", 70)
        vib = sensor_data.get("vibration", 2)
        if status == "CRITICAL":
            return {"chain_of_thought": "Critical limits exceeded.", "risk_assessment": "Imminent failure.", "action_type": "alert", "tools_to_call": [{"tool": "trigger_alert", "params": {"severity": "CRITICAL", "title": "Failure Risk", "details": f"Temp={temp}"}}], "explanation": "Triggered critical alert.", "confidence": 0.95, "expected_outcome": "Maintenance dispatched."}
        return {"chain_of_thought": "Normal ops.", "risk_assessment": "Low.", "action_type": "monitor", "tools_to_call": [], "explanation": "Monitoring.", "confidence": 0.9, "expected_outcome": "Stable."}

    def _execute_tools(self, machine_id: str, decision: dict, sensor_data: dict) -> list:
        results = []
        tools_to_call = decision.get("tools_to_call", [])
        if not tools_to_call:
            return [{"tool": "monitor_only", "success": True, "message": "✅ Monitoring in progress."}]
        tool_map = {
            "adjust_cooling_system": adjust_cooling_system, "adjust_power_level": adjust_power_level,
            "adjust_rpm": adjust_rpm, "schedule_maintenance": schedule_maintenance, "trigger_alert": trigger_alert,
        }
        for tc in tools_to_call:
            tname = tc.get("tool", "")
            params = tc.get("params", {})
            if tname in tool_map:
                try: results.append(tool_map[tname](machine_id, **params))
                except Exception as e: results.append({"tool": tname, "success": False, "message": str(e)})
            else: results.append({"tool": tname, "success": False, "message": f"Unknown tool: {tname}"})
        return results

    def chat(self, user_message: str, machine_id: Optional[str] = None) -> str:
        if not self.client: return "System offline. Check API Key."
        prompt = f"Operator Question: {user_message}\nMachine context: {machine_id}"
        try:
            res = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are ecoSential AI-Pro, an industrial AI assistant. Be professional and concise."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192", temperature=0.5
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"Error connecting to AI: {e}"
