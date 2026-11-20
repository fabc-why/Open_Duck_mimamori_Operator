try:
    from ..process_manager import ProcessManager
except ImportError:
    from process_manager import ProcessManager


SEEK_PYTHON = "/home/openduck/openduck_function/seek/.venv/bin/python"
SEEK_SCRIPT = "/home/openduck/openduck_function/seek/src/seek_person.py"


def come_here(operation: dict, process_manager: ProcessManager, command_publisher=None) -> None:
    try:
        process = process_manager.start_once(SEEK_PYTHON, SEEK_SCRIPT)
    except OSError as error:
        print(f"Failed to start seek process: {error}")
        return

    if process is None:
        print("Seek process is already running")
        return

    target = operation.get("target")
    if target is not None:
        print(f"Started seek process for target: {target} (pid={process.pid})")
    else:
        print(f"Started seek process (pid={process.pid})")
