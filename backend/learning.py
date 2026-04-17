"""
ecoSential AI-Pro — Learning System
Implements self-improving loop:
  - Reward calculation
  - Pattern detection from historical decisions
  - Behavioral strategy adaptation
"""

import numpy as np
from collections import defaultdict
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# REWARD ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_reward(
    sensor_data: dict,
    action_type: str,
    action_result: dict,
    before_health: float,
    after_health_estimate: float,
) -> tuple[float, str]:
    """
    Calculate a numeric reward signal for an agent decision.
    
    Reward logic:
      +5 to +10 : Correct preventive action taken (caught issue before failure)
      +1 to +4  : Correct monitoring (no action needed, system stable)
       0        : Neutral (uncertain outcome)
      -1 to -5  : Wrong action (acted when not needed, wasted resources)
      -5 to -10 : Missed critical event (no action taken despite warning/critical)
    
    Returns:
        (reward: float, rationale: str)
    """
    status = sensor_data.get("status", "NORMAL")
    risk = sensor_data.get("risk_level", "LOW")
    health = sensor_data.get("health_score", 100)

    if status == "CRITICAL":
        if action_type in ("alert", "adjust_params", "maintenance"):
            reward = 8.0 + (after_health_estimate - before_health) * 0.1
            rationale = "✅ Correctly identified and responded to CRITICAL state."
        else:
            reward = -8.0
            rationale = "❌ Failed to act on CRITICAL machine state — dangerous negligence."

    elif status == "WARNING":
        if action_type in ("alert", "adjust_params"):
            reward = 5.0
            rationale = "✅ Proactively intervened on WARNING state — preventive success."
        elif action_type == "monitor":
            reward = 0.5
            rationale = "⚠️ Chose to monitor a WARNING state — marginally acceptable."
        else:
            reward = -2.0
            rationale = "❌ No response to WARNING — risk of escalation."

    else:  # NORMAL
        if action_type == "monitor":
            reward = 3.0
            rationale = "✅ Correctly identified NORMAL state and conserved resources."
        elif action_type in ("alert", "adjust_params"):
            reward = -3.0
            rationale = "⚠️ Unnecessary intervention on NORMAL state — false alarm cost."
        else:
            reward = 1.0
            rationale = "✅ No action needed, system running optimally."

    # Efficiency bonus: faster decisions are better
    if action_result.get("success"):
        reward += 0.5  # small bonus for successful tool execution

    return round(float(reward), 2), rationale


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN DETECTOR
# ─────────────────────────────────────────────────────────────────────────────

class PatternDetector:
    """
    Analyzes the reward history to detect recurring patterns in machine behavior.
    Provides behavioral suggestions to the agent.
    """

    def __init__(self):
        self.machine_stats: dict[str, list[float]] = defaultdict(list)
        self.action_performance: dict[str, list[float]] = defaultdict(list)

    def record(self, machine_id: str, action_type: str, reward: float):
        """Record a new reward event."""
        self.machine_stats[machine_id].append(reward)
        self.action_performance[action_type].append(reward)

    def get_best_action_for_status(self, status: str) -> Optional[str]:
        """Based on history, which action type works best for a given status?"""
        # This is simplified; a real system would use a lookup table updated via RL
        defaults = {
            "CRITICAL": "alert",
            "WARNING": "adjust_params",
            "NORMAL": "monitor",
        }
        return defaults.get(status, "monitor")

    def get_machine_trend(self, machine_id: str) -> str:
        """Summarize the performance trend for a machine."""
        rewards = self.machine_stats.get(machine_id, [])
        if len(rewards) < 3:
            return "Insufficient data for trend analysis."
        
        recent = rewards[-5:]
        avg = np.mean(recent)
        trend_dir = "improving" if recent[-1] > recent[0] else "declining"
        
        if avg > 4:
            return f"🟢 {machine_id} decisions are EXCELLENT (avg reward: {avg:.1f}), trend: {trend_dir}"
        elif avg > 1:
            return f"🟡 {machine_id} decisions are GOOD (avg reward: {avg:.1f}), trend: {trend_dir}"
        else:
            return f"🔴 {machine_id} decisions are POOR (avg reward: {avg:.1f}), trend: {trend_dir} — revisiting strategy"

    def get_insights(self) -> list[str]:
        """Generate human-readable learning insights."""
        insights = []
        
        for machine_id, rewards in self.machine_stats.items():
            if len(rewards) >= 5:
                trend = np.polyfit(range(len(rewards)), rewards, 1)[0]
                if trend > 0.3:
                    insights.append(f"📈 Agent is learning better responses for {machine_id}")
                elif trend < -0.3:
                    insights.append(f"📉 Agent performance on {machine_id} degrading — review patterns")

        for action, rewards in self.action_performance.items():
            if len(rewards) >= 3:
                avg = np.mean(rewards)
                if avg < 0:
                    insights.append(f"⚠️ Action '{action}' is consistently scoring negative — over-triggering?")

        if not insights:
            insights.append("🧠 Learning patterns accumulating — more cycles needed for insights.")

        return insights
