from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import asyncio
import sys
import os
import json
import logging
from pathlib import Path

app = FastAPI(title="Web Automation API", version="1.0.0")

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Concurrency & timeout limits
MAX_CONCURRENT_RUNS = int(os.getenv("MAX_CONCURRENT_RUNS", "2"))
RUN_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_RUNS)
DEFAULT_SCRIPT_TIMEOUT = int(os.getenv("SCRIPT_TIMEOUT", "60"))

# Path to automation script
SCRIPT_PATH = Path(__file__).parent / "main.py"

# Request model
class AutomateRequest(BaseModel):
    run: bool
    item: Optional[str] = None
    timeout: Optional[int] = None


@app.post("/automate")
async def automate_task(req: AutomateRequest):
    """
    Triggers automation when {"run": true} is posted.
    Optional: provide 'item' to look up a specific product or override timeout.
    """
    if not req.run:
        return {"status": "skipped", "message": "Automation not triggered. Set run=true to execute."}

    timeout = req.timeout or DEFAULT_SCRIPT_TIMEOUT

    async with RUN_SEMAPHORE:
        env = os.environ.copy()
        if req.item:
            env["ITEM_TO_LOOKUP"] = req.item

        logger.info(f"Starting automation for item: {req.item or 'default'} (timeout={timeout}s)")

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(SCRIPT_PATH),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=str(Path(__file__).parent),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.error("Automation timed out after %s seconds.", timeout)
            try:
                process.kill()
            except Exception:
                logger.exception("Failed to kill timed-out subprocess")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Automation timed out after {timeout} seconds."
            )

        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
        logger.info("Automation finished: returncode=%s stdout_len=%d stderr_len=%d",
                    process.returncode, len(stdout), len(stderr))

        # Parse output
        data = None
        if stdout:
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                data = {"raw_output": stdout}
        elif stderr:
            data = {"error_output": stderr}
        else:
            data = {"error_output": "No output from script."}

        script_status = data.get("status") if isinstance(data, dict) else None

        # Handle responses
        if script_status == "success":
            return {"status": "success", "result": data}

        if script_status == "error" or process.returncode != 0:
            if "message" not in data and stderr:
                data["stderr"] = stderr
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"status": "error", "result": data}
            )

        return {"status": "unknown", "result": data}
