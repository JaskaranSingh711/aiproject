
import os
import sys
import subprocess
import time

def main():
    print("=====================================================")
    print("Starting ecoSential AI-Pro System...")
    print("=====================================================")
    print("Checking dependencies...")
    try:
        import streamlit
        import faiss
        import groq
        import plotly
        import pandas
        import fastapi
        import uvicorn
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
        
    print("Dependencies verified.")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Start FastAPI Backend
    print("Launching REST API Backend (Port 8080)...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8080"],
        cwd=base_dir
    )
    
    # Give the API a second to spin up
    time.sleep(2)
    
    # 2. Start Streamlit Frontend
    print("Launching Streamlit Frontend...")
    app_path = os.path.join(base_dir, "frontend", "app.py")
    
    try:
        # Run Streamlit in the foreground
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
    except KeyboardInterrupt:
        print("\nShutting down ecoSential AI-Pro...")
    finally:
        # Ensure API process is killed when Streamlit exits
        api_process.terminate()
        api_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
