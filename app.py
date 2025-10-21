from fastapi import FastAPI
import asyncio, subprocess, sys, os, json, logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/automate")
async def automate_task(task: dict):
    try:
        script_path = os.path.join(os.path.dirname(__file__), "main.py")

        # How to run script
        def run_script():
            return subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )

        # Run subprocess safely in thread pool 
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_script)

        stdout, stderr = result.stdout.strip(), result.stderr.strip()

        # Try to parse JSON output 
        if stdout:
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                data = {"raw_output": stdout}
        elif stderr:
            data = {"error_output": stderr}
        else:
            data = {"error_output": "No output at all."}

        status = "success" if result.returncode == 0 else "error"
        return {"status": status, "result": data}

    except Exception as e:
        logger.exception("Automation failed")
        return {"status": "error", "message": str(e)}
