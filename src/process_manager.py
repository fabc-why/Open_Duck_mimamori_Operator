import os
import signal
import subprocess
import threading


class ProcessManager:
    def __init__(self) -> None:
        self._processes: set[subprocess.Popen[bytes]] = set()
        self._lock = threading.Lock()

    def start_once(self, executable: str, script: str) -> subprocess.Popen[bytes] | None:
        with self._lock:
            active_processes = {
                process for process in self._processes if process.poll() is None
            }
            self._processes = active_processes
            if active_processes:
                return None

            try:
                process = subprocess.Popen(
                    [executable, script],
                    start_new_session=True,
                )
            except OSError:
                raise

            self._processes.add(process)
            return process

    def stop_all(self) -> None:
        with self._lock:
            processes = list(self._processes)
            self._processes.clear()

        for process in processes:
            if process.poll() is not None:
                continue
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                continue

        for process in processes:
            if process.poll() is not None:
                continue
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    continue
                process.wait()
