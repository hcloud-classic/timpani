from ..net.openssh_command import SSHCommand
from ..exceptions.exception import SSHConnetException, SSHCommandException

class Base():

    @staticmethod
    def ssh_connect(func):
        def wrapped_function(*params, **kwargs):
            ssh = SSHCommand()
            remote_server = kwargs['remote_server']
            # print("test {}".format(remote_server))
            # print("aaaaaaaaaaaaaaaaaaaaaa")
            try:
                ssh_session = ssh.connetion(server=remote_server)
                kwargs['ssh'] = ssh
                kwargs['ssh_session'] = ssh_session
                responses = func(*params, **kwargs)
                # print(responses)
                ssh.disconnetion(ssh_session=ssh_session)
                return responses
            except Exception as e:
                print(e)
                return "FAIL AAAAA"

        return wrapped_function
