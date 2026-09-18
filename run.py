import subprocess
import sys
import time

def run():
    print("Starting FastAPI backend on http://127.0.0.1:8000...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    )

    # Wait briefly to let backend start up
    time.sleep(2)

    print("API Swagger documentation available at http://127.0.0.1:8000/docs")

    print("Starting Streamlit UI on http://localhost:8501...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"],
    )

    try:
        # Keep the main process alive
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    run()
