"""
ecoSential AI-Pro — Industrial Tool Layer
All external actions the agent can call. Each tool returns a structured result dict.
Tools are categorized:
  - Sensor Tools: Read data
  - Control Tools: Adjust machine parameters
  - Alert Tools: Notify maintenance teams
  - Analysis Tools: Run analytics
"""

from datetime import datetime
import random
import math


# ─────────────────────────────────────────────────────────────────────────────
# SENSOR TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def read_machine_sensors(machine_id: str, sensor_data: dict) -> dict:
    """
    Wrapper that formats raw sensor data into a structured tool result.
    In production, this would call the actual PLC/SCADA API.
    """
    return {
        "tool": "read_machine_sensors",
        "machine_id": machine_id,
        "success": True,
        "data": sensor_data,
        "message": f"Successfully read {len(sensor_data)} sensor channels from {machine_id}",
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def adjust_cooling_system(machine_id: str, cooling_rate: float) -> dict:
    """
    Adjust the cooling system fan speed (%).
    cooling_rate: 0–100 percent
    """
    cooling_rate = max(0, min(100, cooling_rate))
    estimated_temp_reduction = cooling_rate * 0.18  # °C reduction estimate
    
    return {
        "tool": "adjust_cooling_system",
        "machine_id": machine_id,
        "success": True,
        "parameter": "cooling_rate",
        "new_value": f"{cooling_rate}%",
        "estimated_effect": f"Expected temperature reduction: -{estimated_temp_reduction:.1f}°C in ~5 min",
        "message": f"✅ Cooling system on {machine_id} set to {cooling_rate}%",
        "timestamp": datetime.now().isoformat(),
    }


def adjust_power_level(machine_id: str, power_pct: float) -> dict:
    """
    Throttle machine power output (%).
    power_pct: 0–100 percent
    """
    power_pct = max(20, min(100, power_pct))
    energy_saving = 100 - power_pct
    
    return {
        "tool": "adjust_power_level",
        "machine_id": machine_id,
        "success": True,
        "parameter": "power_level",
        "new_value": f"{power_pct}%",
        "estimated_effect": f"Estimated energy saving: ~{energy_saving:.0f}% reduction",
        "message": f"⚡ Power level on {machine_id} throttled to {power_pct}%",
        "timestamp": datetime.now().isoformat(),
    }


def adjust_rpm(machine_id: str, target_rpm: float) -> dict:
    """
    Adjust machine RPM to reduce vibration or improve efficiency.
    """
    return {
        "tool": "adjust_rpm",
        "machine_id": machine_id,
        "success": True,
        "parameter": "rpm",
        "new_value": f"{target_rpm:.0f} RPM",
        "estimated_effect": f"Vibration expected to normalize within 2–3 minutes",
        "message": f"🔄 RPM on {machine_id} adjusted to {target_rpm:.0f}",
        "timestamp": datetime.now().isoformat(),
    }


def schedule_maintenance(machine_id: str, priority: str, reason: str) -> dict:
    """
    Schedule a maintenance event.
    priority: "URGENT" | "HIGH" | "ROUTINE"
    """
    ticket_id = f"MNT-{random.randint(10000, 99999)}"
    schedule_map = {
        "URGENT": "Within 1 hour",
        "HIGH": "Within 4 hours",
        "ROUTINE": "Next maintenance window (48h)",
    }
    
    return {
        "tool": "schedule_maintenance",
        "machine_id": machine_id,
        "success": True,
        "ticket_id": ticket_id,
        "priority": priority,
        "schedule": schedule_map.get(priority, "Next window"),
        "reason": reason,
        "message": f"🔧 Maintenance ticket {ticket_id} created — {priority} priority",
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ALERT TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def trigger_alert(machine_id: str, severity: str, title: str, details: str) -> dict:
    """
    Trigger a real-time alert. Severity: CRITICAL | WARNING | INFO
    In production, this would call Twilio, PagerDuty, or Slack API.
    """
    alert_id = f"ALT-{random.randint(1000, 9999)}"
    channels = {
        "CRITICAL": ["SMS", "Email", "PagerDuty", "Control Room Display"],
        "WARNING": ["Email", "Slack"],
        "INFO": ["Dashboard"],
    }
    
    return {
        "tool": "trigger_alert",
        "machine_id": machine_id,
        "success": True,
        "alert_id": alert_id,
        "severity": severity,
        "title": title,
        "details": details,
        "notified_channels": channels.get(severity, ["Dashboard"]),
        "message": f"🚨 Alert {alert_id} sent via {', '.join(channels.get(severity, ['Dashboard']))}",
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_energy_efficiency(machine_id: str, energy_kw: float, output_units: float = None) -> dict:
    """Calculate energy efficiency index for a machine."""
    if output_units is None:
        output_units = random.uniform(80, 120)  # Simulated production output
    
    efficiency = (output_units / energy_kw) * 100 if energy_kw > 0 else 0
    benchmark = 55.0  # Industry benchmark
    delta = efficiency - benchmark
    
    return {
        "tool": "calculate_energy_efficiency",
        "machine_id": machine_id,
        "success": True,
        "energy_kw": energy_kw,
        "output_units": round(output_units, 2),
        "efficiency_index": round(efficiency, 2),
        "benchmark": benchmark,
        "delta_vs_benchmark": round(delta, 2),
        "rating": "EXCELLENT" if delta > 10 else "GOOD" if delta > 0 else "POOR",
        "message": f"📊 Energy efficiency: {efficiency:.1f} (Benchmark: {benchmark})",
        "timestamp": datetime.now().isoformat(),
    }


def predict_failure_window(machine_id: str, current_vib: float, current_temp: float, health_score: float) -> dict:
    """
    Simple physics-based failure prediction model.
    Returns estimated time to failure in hours.
    """
    # Model: higher temp + vib = faster degradation
    degradation_rate = (max(0, current_temp - 70) * 0.02) + (max(0, current_vib - 2) * 0.05)
    
    if health_score <= 0:
        ttf = 0
    elif degradation_rate <= 0:
        ttf = float('inf')
    else:
        ttf = (health_score / 100) / degradation_rate  # hours
        ttf = min(ttf, 720)  # Cap at 30 days
    
    if ttf < 4:
        urgency = "IMMINENT"
        recommended_action = "Halt machine and inspect immediately"
    elif ttf < 24:
        urgency = "URGENT"
        recommended_action = "Schedule maintenance within 4 hours"
    elif ttf < 72:
        urgency = "MODERATE"
        recommended_action = "Plan maintenance this week"
    else:
        urgency = "LOW"
        recommended_action = "Continue monitoring, next scheduled check"
    
    return {
        "tool": "predict_failure_window",
        "machine_id": machine_id,
        "success": True,
        "estimated_ttf_hours": round(ttf, 1) if ttf != float('inf') else "720+",
        "urgency": urgency,
        "recommended_action": recommended_action,
        "confidence": "85%",  # Simulated model confidence
        "message": f"🔮 Predicted TTF: {ttf:.0f}h — {urgency}",
        "timestamp": datetime.now().isoformat(),
    }


def get_kpi_summary(machines_data: list[dict]) -> dict:
    """Aggregate KPIs across all machines."""
    if not machines_data:
        return {}
    
    temps = [m.get("temperature", 0) for m in machines_data]
    vibs = [m.get("vibration", 0) for m in machines_data]
    energies = [m.get("energy_consumption", 0) for m in machines_data]
    health_scores = [m.get("health_score", 0) for m in machines_data]
    
    critical_count = sum(1 for m in machines_data if m.get("status") == "CRITICAL")
    warning_count = sum(1 for m in machines_data if m.get("status") == "WARNING")
    
    return {
        "fleet_health_avg": round(sum(health_scores) / len(health_scores), 1),
        "total_energy_kw": round(sum(energies), 1),
        "critical_machines": critical_count,
        "warning_machines": warning_count,
        "avg_temperature": round(sum(temps) / len(temps), 1),
        "avg_vibration": round(sum(vibs) / len(vibs), 2),
        "machines_monitored": len(machines_data),
        "overall_status": "CRITICAL" if critical_count > 0 else "WARNING" if warning_count > 0 else "NORMAL",
    }
