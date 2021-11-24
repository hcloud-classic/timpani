import paramiko
import io
from ..exceptions.exception import SSHCommandException, SSHConnetException
from paramiko.ssh_exception import SSHException

class SSHCommand():
    RSA_PATH = '/root/.ssh/id_rsa'

    def __init__(self, password=None, pkey=None):
        self.username = 'root'
        self.password = password
        print(self.RSA_PATH)
        self.pkey = paramiko.RSAKey.from_private_key_file(self.RSA_PATH)


    def connetion(self, server):

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.password is not None:
                ssh.connect(hostname=server, username=self.username, password=self.password)
            elif self.pkey is not None:
                ssh.connect(hostname=server, username=self.username, pkey=self.pkey)
        except SSHException as e:
            # Connection Failed
            msg = "SSH CONNETION ERROR [SERVER : {}]".format(server)
            raise SSHConnetException(msg)
        print('connetion success')
        return ssh

    def ssh_execute(self, ssh_session, command, is_print=True):

        # exit_status=0
        # mark="ssh_helper_result_mark!!@@="
        # command=command+";echo " + mark + "$?"
        print("RUN COMMAND : {}".format(command))
        try:
            stdin, stdout, stderr = ssh_session.exec_command(command)
        except Exception as e:
            print(e)
            msg = "SSH RUNTIME ERROR [COMMAND : {}]".format(command)
            raise SSHCommandException(msg)

        return stdin, stdout, stderr

    def disconnetion(self, ssh_session):
        ssh_session.close()
