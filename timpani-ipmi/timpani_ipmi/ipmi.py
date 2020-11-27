import subprocess
import os
from .command import _Command

class IPMIManager(object):

    @staticmethod
    def get_ipmi_system_uuid(addr: str, user: str, password: str):
        shell_cmd = "ipmitool -H {addr} -U {user} -P {password} mc guid".format(addr=addr, user=user, password=password)
        try:
            output= _Command.shell_run(shell_cmd)
            res = output.split(':')
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to IPMI Connection\n{e.output}\n")

        return res
