try:
    from ..process_manager import ProcessManager
except ImportError:
    from process_manager import ProcessManager

import roslibpy


STOP_COMMAND = "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"


def stop(operation: dict, process_manager: ProcessManager, command_publisher=None) -> None:
    process_manager.stop_all()
    if command_publisher is not None:
        command_publisher.publish(
            roslibpy.Message({"data": STOP_COMMAND})
        )
    print("Stopped all subprocesses")
