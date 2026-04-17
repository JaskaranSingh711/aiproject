# 🏭 ecoSential AI-Pro

**Theme:** Autonomous + Memory + Learning Industrial Intelligence System

## 🎤 Elevator Pitch (30 seconds)
"Factories lose billions annually to unplanned downtime and energy waste. Current systems just alert you *after* something breaks. **ecoSential AI-Pro** is an autonomous AI agent that doesn't just monitor—it thinks, acts, and learns. By combining real-time sensor data with long-term vector memory and reinforcement learning loops, it predicts failures, autonomously adjusts machine parameters, and continuously improves its own decision-making. It’s not a dashboard; it’s your smartest digital factory manager."

## 🚨 Problem Statement
Industrial manufacturing relies on static thresholds for alerts. This leads to:
1. **Alarm Fatigue:** Too many false positives.
2. **Reactive Maintenance:** Fixing things after they break, causing costly downtime.
3. **Knowledge Loss:** When senior operators leave, their intuition about machine behavior leaves with them.

## 💡 Solution Uniqueness
- **Autonomous Action:** Doesn't just plot charts; it triggers API calls to adjust cooling rates or power levels dynamically.
- **Experience Replay (Memory):** Uses FAISS vector DB to recall *past* similar states and applies what worked best, exactly like a seasoned engineer.
- **Self-Improving Loop:** Evaluates the outcome of its actions and assigns a reward, updating its future behavior without human code changes.

## 🎬 Demo Script for Judges
1. **The Setup:** "Here is our factory floor. Machine M-101 is running hot."
2. **The Observation:** Click 'Trigger AI Analysis'. Show the judges the sensor data.
3. **The Brain:** Point to the "Agent Reasoning Process". "Look, the LLM is explicitly reasoning about the high temperature and comparing it to past memories."
4. **The Action:** Show the action taken (e.g., *Adjusted Machine M-101: Cooling=80%*).
5. **The Memory:** Scroll down to the Experience Replay table. "And here, it stored the outcome. The next time M-101 acts up, the agent will remember this exact intervention and do it faster."

## 🚀 Future Scope (Startup Vision)
- **Multi-Agent Swarms:** Dedicated agents for Energy, Maintenance, and Supply Chain negotiating with each other.
- **Edge Deployment:** Running compressed models directly on PLC controllers.
- **Digital Twin Integration:** Simulating actions in a 3D environment before executing them in the real world.

## 🛠️ How to Run
```bash
cd ecoSential
pip install -r requirements.txt
# Add your Gemini API key to .env (cp .env.example .env)
streamlit run frontend/app.py
```
