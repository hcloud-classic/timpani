import itertools
import os
import subprocess

from typing import List

class _Command:

    def __init__(self, sub_command:str, options:List = None,
                 properties:List[str] = None,
                 targets:List[str] = None,
                 main_command:str = "zfs",
                 env_variables_override: dict = None
                 ):
        self.main_command = main_command
        self.sub_command = sub_command
        self.targets = targets
        self.env_variables_override = env_variables_override
        self.call_variables_override = env_variables_override

        self.call_args = [o for o in options] if options is not None else []
        self.shell_command = None

        if properties:
            self.properties = self._prepare_properties(properties)



    @staticmethod
    def _prepare_properties(properties: List[str]):
        if properties is not None:
            prop_list = [["-o", prop] for prop in properties]
            return list(itertools.chain.from_iterable(prop_list))
        return []

    def argcheck_depth(self, depth):
        if depth is not None:
            if depth < 0:
                raise RuntimeError("Depth cannot be negative")
            self.call_args.extend(["-d", str(depth)])

    def argcheck_columns(self, columns: list):
        if columns:
            if "all" in columns:
                self.call_args.extend("-o","all")
            else:
                self.call_args.extend("-o", ",".join(columns))

    def set_shellcommand(self, command:str):
        self.shell_command = command

    def run(self):

        new_env = dict(os.environ)

        if self.env_variables_override:
            for key, value in self.env_variables_override.items():
                new_env[key] = value

        arguments = self.call_args

        if hasattr(self, 'properties') and self.properties:
            arguments.extend(self.properties)

        if hasattr(self, 'targets') and self.targets:
            arguments.extend(self.targets)

        zfs_call = [self.main_command, self.sub_command] + arguments
        try:
            output = subprocess.check_output(zfs_call, universal_newlines=True, stderr=subprocess.PIPE, env=new_env)
        except subprocess.CalledProcessError as e:
            raise e

        return output

    @staticmethod
    def shell_run(shell_cmd, file_fd=None):

        try:
            if file_fd is None:
                output = subprocess.run(shell_cmd, universal_newlines=True, stderr=subprocess.PIPE, shell=True)
            else:
                output = subprocess.run(shell_cmd, universal_newlines=True, stderr=subprocess.PIPE, stdout=file_fd)
        except subprocess.CalledProcessError as e:
            raise e

        return output