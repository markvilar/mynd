"""Main entrypoint for the command-line interface."""

from ..runtime import Command, command_line_arguments
from ..utils.log import logger

from .ingestion import invoke_project_setup
from .reconstruction import invoke_reconstruct_task
from .registration import invoke_registration_task


def main():
    """Runs the command-line interface."""

    command: Command = command_line_arguments()

    match command:
        case Command(command="create"):
            invoke_project_setup(command)
        case Command(command="summarize"):
            raise NotImplementedError("summarize command is not implemented")
        case Command(command="reconstruct"):
            invoke_reconstruct_task(command)
        case Command(command="register"):
            invoke_registration_task(command)
        case _:
            logger.warning(f"invalid command: {command}")


if __name__ == "__main__":
    main()
