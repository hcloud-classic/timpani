import logging
import paramiko
from scp import SCPClient, SCPException

logger = logging.getLogger(__name__)

class SSHManager(object):

    def __init__(self):
        self.ssh_client = None

    def create_ssh_client(self, hostname, username, port=22, password=None, host_key=None):
        """Create SSH client session to remote server"""
        logger.info("Create SSH Client")
        print("Create SSH Client")
        is_key = False if host_key is None else True
        is_password = False if password is None else True

        if self.ssh_client is None:
            self.ssh_client = paramiko.SSHClient()
            if is_key:
                keyObj = paramiko.RSAKey(data=paramiko.py3compat.decodebytes(host_key.encode()))
                self.ssh_client.get_host_keys().add(hostname=hostname, keytype="ssh-rsa", key=keyObj)
                self.ssh_client.connect(hostname=hostname, port=port, username=username)
            elif is_password:
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(hostname=hostname, username=username, password=password, port=port)
            else:
                self.ssh_client = None
                logger.info("SSH client Connection Failed")
        else:
            logger.info("SSH client session exist.")

        logger.info("is_key : {}, is_password : {}".format(is_key, is_password))
        print("is_key : {}, is_password : {}".format(is_key, is_password))

    def close_ssh_client(self):
        """Close SSH client session"""
        self.ssh_client.close()

    def send_file(self, local_path, remote_path):
        """Send a single file to remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(localpath=local_path, remotepath=remote_path, preserve_time=True)
        except SCPException:
            raise SCPException.message

    def get_file(self, remote_path, local_path):
        """Get a single file from remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.get(remote_path, local_path)
        except SCPException:
            raise SCPException.message

    def send_command(self, command):
        """Send a single command"""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.readlines()