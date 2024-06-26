"""Entry point for the create task."""

from loguru import logger

from benthoscan.tasks.create import invoke_project_setup
from benthoscan.tasks.reconstruct import invoke_reconstruct_task

from .command import Command, command_line_arguments


def main():
    """Create task entry point."""

    command: Command = command_line_arguments()

    logger.info(f"Command: {command}")

    match command:
        case Command(command="create"):
            invoke_project_setup(command)
        case Command(command="summarize"):
            raise NotImplementedError("summarize command is not implemented")
        case Command(command="reconstruct"):
            invoke_reconstruct_task(command)
        case Command(command="register"):
            raise NotImplementedError("register command is not implemented")
        case _:
            logger.warning(f"invalid command: {command}")


if __name__ == "__main__":
    main()
