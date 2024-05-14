"""Entry point for the create task."""

from loguru import logger

from benthoscan.tasks.create import handle_create_task

from .command import Command, command_line_arguments


def main():
    """Create task entry point."""

    command: Command = command_line_arguments()

    logger.info(f"Command: {command}")

    match command:
        case Command(command="create"):
            handle_create_task(command)
        case Command(command="summarize"):
            raise NotImplementedError("summarize command is not implemented")
        case Command(command="reconstruct"):
            raise NotImplementedError("reconstruct command is not implemented")
        case Command(command="register"):
            raise NotImplementedError("register command is not implemented")
        case _:
            logger.warning(f"invalid command: {command}")


if __name__ == "__main__":
    main()
