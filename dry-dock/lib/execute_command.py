import os
import subprocess


class ExecuteCommand:

    def __init__(self, command, environment=None):
        self.command = command
        self.environment = environment

        params = {'stderr': subprocess.PIPE,
                  'stdout': subprocess.PIPE}

        if self.environment:
            if 'PATH' not in self.environment:
                self.environment['PATH'] = os.environ['PATH']

            params['env'] = self.environment

        self.result = subprocess.run(self.command, **params)
        self.result.stderr = self.result.stderr.decode("utf-8").splitlines()
        self.result.stdout = self.result.stdout.decode("utf-8").splitlines()

        return
