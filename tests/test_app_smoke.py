import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def test_application_starts_and_serves_health(tmp_path):
    port = _free_tcp_port()
    database_path = tmp_path / "smoke.db"
    project_root = Path(__file__).resolve().parent.parent
    url = f"http://127.0.0.1:{port}/health"

    environment = os.environ.copy()
    environment.update(
        {
            "APP_ENV": "testing",
            "DB_NAME": str(database_path),
            "PYTHONPATH": str(project_root),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=project_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        response_body = _wait_for_health(url, process)
    finally:
        _stop_process(process)

    assert response_body == '{"status":"ok"}'
    assert database_path.exists()


def _free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_for_health(url: str, process: subprocess.Popen[str]) -> str:
    deadline = time.monotonic() + 10
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise AssertionError(
                f"Application exited before serving /health.\n"
                f"stdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )

        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                assert response.status == 200
                return response.read().decode("utf-8")
        except (ConnectionError, TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            time.sleep(0.2)

    raise AssertionError(f"Application did not serve /health in time: {last_error}")


def _stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
