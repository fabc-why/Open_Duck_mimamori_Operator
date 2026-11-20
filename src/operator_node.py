import json
import time

import roslibpy
from roslibpy.core import RosTimeoutError

try:
    from .commands import COMMAND_HANDLERS
    from .process_manager import ProcessManager
except ImportError:
    from commands import COMMAND_HANDLERS
    from process_manager import ProcessManager


TOPIC = "/openduck/operation/actions"
COMMAND_TOPIC = "/openduck/commands"
STOP_COMMAND = "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"


class OperationNode:
    def __init__(self, host: str = "localhost", port: int = 9090) -> None:
        self._process_manager = ProcessManager()
        self._client = roslibpy.Ros(host=host, port=port)
        self._client.run()
        self._subscription = roslibpy.Topic(
            self._client,
            TOPIC,
            "std_msgs/String",
        )
        self._subscription.subscribe(self._operation_callback)
        self._command_publisher = roslibpy.Topic(
            self._client,
            COMMAND_TOPIC,
            "std_msgs/String",
        )
        self._command_publisher.advertise()
        print(f"Subscribed to {TOPIC}")

    def _operation_callback(self, message: dict) -> None:
        data = message.get("data")
        if not isinstance(data, str):
            print("Invalid ROS message: 'data' must be a string")
            return
        try:
            operation = json.loads(data)
        except json.JSONDecodeError as error:
            print(f"Invalid JSON: {error}")
            return

        if not isinstance(operation, dict):
            print("Operation must be a JSON object")
            return

        command = operation.get("command")
        if not isinstance(command, str) or not command:
            print("Operation requires a non-empty string 'command'")
            return

        handler = COMMAND_HANDLERS.get(command)
        if handler is None:
            print(f"Unknown command: {command}")
            return
        handler(operation, self._process_manager, self._command_publisher)

    def cleanup(self) -> None:
        self._process_manager.stop_all()
        self._subscription.unsubscribe()
        self._client.terminate()

    def is_running(self) -> bool:
        return self._client.is_connected

    def loop(self) -> None:
        try:
            while self.is_running():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


def main() -> None:
    try:
        node = OperationNode()
        node.loop()
    except RosTimeoutError as error:
        print(f"Failed to connect to rosbridge: {error}")


if __name__ == "__main__":
    main()
