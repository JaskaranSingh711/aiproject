"""
ecoSential AI-Pro — Data Generator
Simulates realistic industrial sensor data for machines.
Supports: normal operation, gradual degradation, sudden failures, anomaly injection.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Machine configurations — each machine has its own baseline behavior
MACHINE_CONFIGS = {
    "M-101": {
        "name": "CNC Milling Machine Alpha",
        "type": "CNC",
        "baseline_temp": 72.0,
        "baseline_vib": 2.5,
        "baseline_energy": 180.0,
        "baseline_pressure": 4.5,
        "baseline_rpm": 1800,
        "degradation_rate": 0.003,
        "icon": "⚙️",
    },
    "M-102": {
        "name": "Hydraulic Press Beta",
        "type": "Hydraulic",
        "baseline_temp": 65.0,
        "baseline_vib": 1.8,
        "baseline_energy": 320.0,
        "baseline_pressure": 8.2,
        "baseline_rpm": 1200,
        "degradation_rate": 0.005,
        "icon": "🔧",
    },
    "M-205": {
        "name": "Conveyor Motor Gamma",
        "type": "Conveyor",
        "baseline_temp": 58.0,
        "baseline_vib": 1.2,
        "baseline_energy": 95.0,
        "baseline_pressure": 2.1,
        "baseline_rpm": 960,
        "degradation_rate": 0.002,
        "icon": "🏗️",
    },
    "M-301": {
        "name": "Industrial Pump Delta",
        "type": "Pump",
        "baseline_temp": 78.0,
        "baseline_vib": 3.1,
        "baseline_energy": 220.0,
        "baseline_pressure": 6.8,
        "baseline_rpm": 2400,
        "degradation_rate": 0.007,
        "icon": "💧",
    },
}


def get_sensor_data(machine_id: str, cycle_count: int = 0, inject_anomaly: bool = False) -> dict:
    """
    Generate a realistic sensor reading for a given machine.
    
    Args:
        machine_id: The machine identifier (e.g., "M-101")
        cycle_count: Number of cycles run, used to simulate gradual degradation
        inject_anomaly: If True, forcefully injects a critical anomaly for demo purposes
    
    Returns:
        Dict containing all sensor readings + metadata
    """
    if machine_id not in MACHINE_CONFIGS:
        machine_id = "M-101"  # Default fallback
    
    config = MACHINE_CONFIGS[machine_id]
    degradation = 1.0 + (config["degradation_rate"] * cycle_count)
    
    # Gaussian noise factor
    noise = lambda std: np.random.normal(0, std)
    
    if inject_anomaly:
        # Force a critical scenario for demo
        temp = config["baseline_temp"] * degradation + random.uniform(25, 40)
        vib = config["baseline_vib"] * degradation + random.uniform(5, 9)
        energy = config["baseline_energy"] * degradation * random.uniform(1.3, 1.6)
        pressure = config["baseline_pressure"] * random.uniform(1.4, 1.8)
        rpm = config["baseline_rpm"] * random.uniform(0.7, 0.85)
    else:
        temp = config["baseline_temp"] * degradation + noise(4.0)
        vib = config["baseline_vib"] * degradation + noise(0.5)
        energy = config["baseline_energy"] * degradation + noise(15.0)
        pressure = config["baseline_pressure"] + noise(0.3)
        rpm = config["baseline_rpm"] + noise(50)
    
    # Derived health score (0–100, higher is better)
    temp_score = max(0, 100 - max(0, temp - 85) * 3)
    vib_score = max(0, 100 - max(0, vib - 3) * 8)
    health_score = round((temp_score * 0.5 + vib_score * 0.5), 1)
    
    # Operational status based on thresholds
    if temp > 100 or vib > 8.0:
        status = "CRITICAL"
        risk_level = "HIGH"
    elif temp > 88 or vib > 5.5:
        status = "WARNING"
        risk_level = "MEDIUM"
    else:
        status = "NORMAL"
        risk_level = "LOW"
    
    return {
        "machine_id": machine_id,
        "machine_name": config["name"],
        "machine_type": config["type"],
        "icon": config["icon"],
        "timestamp": datetime.now().isoformat(),
        "temperature": round(float(temp), 2),
        "vibration": round(float(max(0, vib)), 2),
        "energy_consumption": round(float(max(0, energy)), 2),
        "pressure": round(float(max(0, pressure)), 2),
        "rpm": round(float(max(0, rpm)), 0),
        "health_score": health_score,
        "status": status,
        "risk_level": risk_level,
        "cycle_count": cycle_count,
    }


def get_historical_data(machine_id: str, hours: int = 24, points: int = 144) -> pd.DataFrame:
    """Generate a plausible historical dataset for trend charts."""
    config = MACHINE_CONFIGS.get(machine_id, MACHINE_CONFIGS["M-101"])
    
    now = datetime.now()
    timestamps = [now - timedelta(minutes=(points - i) * (hours * 60 // points)) for i in range(points)]
    
    records = []
    for i, ts in enumerate(timestamps):
        # Simulate a gradual trend with occasional spikes
        progress = i / points
        spike = np.random.rand() < 0.04  # 4% chance of a spike event
        spike_mult = random.uniform(1.15, 1.35) if spike else 1.0
        
        records.append({
            "timestamp": ts,
            "temperature": round(config["baseline_temp"] + np.random.normal(0, 3) * spike_mult + progress * 2, 2),
            "vibration": round(config["baseline_vib"] + np.random.normal(0, 0.4) * spike_mult, 2),
            "energy_consumption": round(config["baseline_energy"] + np.random.normal(0, 12) * spike_mult, 2),
            "health_score": round(max(50, 95 - progress * 15 + np.random.normal(0, 2)), 1),
        })
    
    return pd.DataFrame(records)


def get_all_machines() -> list[dict]:
    """Returns a list of all machine configs for the sidebar."""
    return [
        {"id": mid, **cfg}
        for mid, cfg in MACHINE_CONFIGS.items()
    ]
