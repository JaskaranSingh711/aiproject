"""
ecoSential AI-Pro — FastAPI Service
Provides a production-ready REST API for external systems to interface with the agent.
This makes the project a true industrial AI platform, not just a dashboard.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.agent import AutonomousAgent
from backend.data_generator import MACHINE_CONFIGS

app = FastAPI(
    title="ecoSential AI-Pro API",
    description="REST API for the Autonomous Industrial Intelligence System",
    version="1.0.0"
)

# Global agent instance for the API
# In a real distributed system, we'd use Redis for state, but this works for the hackathon MVP
api_agent = AutonomousAgent()

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class SensorDataInput(BaseModel):
    machine_id: str
    temperature: float
    vibration: float
    energy_consumption: float
    pressure: Optional[float] = None
    rpm: Optional[float] = None
    health_score: float
    status: str

class AgentDecisionResponse(BaseModel):
    machine_id: str
    timestamp: str
    decision: Dict[str, Any]
    tool_results: List[Dict[str, Any]]
    reward: float

class MemoryQuery(BaseModel):
    query_text: str
    top_k: int = 3

# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    """System health check endpoint."""
    return {
        "status": "online",
        "service": "ecoSential AI-Pro API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/machines")
def get_machines():
    """Get a list of all monitored machines and their configurations."""
    return {"machines": MACHINE_CONFIGS}

@app.post("/agent/process", response_model=AgentDecisionResponse)
def process_telemetry(data: SensorDataInput):
    """
    Push new sensor telemetry to the agent.
    The agent will observe, reason, act, and learn based on this data.
    """
    if data.machine_id not in MACHINE_CONFIGS:
        raise HTTPException(status_code=404, detail="Machine ID not recognized")
    
    # Convert Pydantic model to dict
    sensor_dict = data.model_dump()
    
    # Run the full agent loop synchronously
    try:
        result = api_agent.run_cycle(data.machine_id, sensor_dict)
        
        return {
            "machine_id": result["machine_id"],
            "timestamp": result["timestamp"],
            "decision": result["decision"],
            "tool_results": result["tool_results"],
            "reward": result["reward"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

@app.post("/memory/search")
def search_memory(query: MemoryQuery):
    """Search the FAISS vector database for past experiences."""
    try:
        results = api_agent.memory.retrieve_relevant(query.query_text, query.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search error: {str(e)}")

@app.get("/memory/stats")
def memory_statistics():
    """Get analytics on the agent's learning progress."""
    return api_agent.memory.get_stats()
