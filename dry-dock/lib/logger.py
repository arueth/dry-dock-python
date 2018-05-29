import logging
import os
import sys


class Logger(logging.Logger):
    def __init__(self, filename, log_level):
        name = os.path.basename(filename)
        super().__init__(name)

        self.setLevel(logging.getLevelName(log_level))

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)

        self.addHandler(handler)

        return

    def prepare_execution(self, execution):
        return f"{{ returncode: {execution.result.returncode}, " \
               f"stdout: {execution.result.stdout}, " \
               f"stderr: {execution.result.stderr} }}"
