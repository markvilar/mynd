"""Module for redirecting system I/O."""

import os
import sys
from contextlib import contextmanager

@contextmanager
def stdout_redirected(sink_path: str=os.devnull):
    """Redirects the stdout sink to the given file descriptor within a context,
    before restoring it to the original descriptor.

    Adapted from:
    https://stackoverflow.com/questions/5081657/how-do-i-prevent-a-c-shared-library-to-print-on-stdout-in-python/17954769#17954769
    
    Example usage:
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    """
    old_file_descriptor = sys.stdout.fileno()

    #### # assert that Python and C stdio write using the same file descriptor
    #### assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

    def _redirect_stdout(sink_path: str):
        """TODO"""
        sys.stdout.close() # + implicit flush()
        os.dup2(sink_path.fileno(), old_file_descriptor) # fd writes to 'to' file
        sys.stdout = os.fdopen(old_file_descriptor, 'w') # Python writes to fd


    with os.fdopen(os.dup(old_file_descriptor), 'w') as old_stdout:
        with open(sink_path, 'w') as file:
            _redirect_stdout(sink_path=file)
        try:
            yield # allow code to be run with the redirected stdout
        finally:
            # restore stdout, buffering and flags such as, CLOEXEC may be different
            _redirect_stdout(sink_path=old_stdout)
