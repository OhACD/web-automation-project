from typing import Union
from fastapi import FastAPI
import asyncio, subprocess, sys, os, json, logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/automate/{run_status}")
async def automate_task(run_status: Union[bool, None], task: dict):
    """
    Triggers automation only if either:
      - URL path param run_status=True 
      - JSON body contains "run": true
    """
    try:
        # Whether the automation should run or not
        should_run = bool(run_status) or task.get("run", False)

        if not should_run:
            return {
                "status": "skipped",
                "message": "Automation not triggered. Set run_status=true or include 'run': true in JSON."
            }

        # Path to PlayWright script
        script_path = os.path.join(os.path.dirname(__file__), "main.py")

        # How to run the Script
        def run_script():
            return subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )

        # Run subprocess asynchronously
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_script)

        stdout, stderr = result.stdout.strip(), result.stderr.strip()

        # Try parsing JSON output
        if stdout:
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                data = {"raw_output": stdout}
        elif stderr:
            data = {"error_output": stderr}
        else:
            data = {"error_output": "No output at all."}

        if isinstance(data, dict) and data.get("status") == "success":
            status = "success"
        elif result.returncode != 0:
            status = "error"
        else:
            status = "error" if data.get("status") == "error" else "success"

        return {"status": status, "result": data}

    except Exception as e:
        logger.exception("Automation failed")
        return {"status": "error", "message": str(e)}