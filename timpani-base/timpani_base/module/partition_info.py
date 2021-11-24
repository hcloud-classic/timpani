from .base import Base
import json
import os
import select
from contextlib import contextmanager

class PartitionInfo():

    RECV_BUFFER = 1024*1024*10
    # DISK DEVICE SEARCH (UBUNTU)
    @Base.ssh_connect
    def lsblk_dev_list(self, remote_server=None, ssh=None, ssh_session=None):
        # lsblk -o NAME,KNAME,FSTYPE,MOUNTPOINT,LABEL,UUID,SUBSYSTEMS,TRAN,TYPE -d -J
        command = "lsblk -o NAME,KNAME,FSTYPE,MOUNTPOINT,LABEL,UUID,SUBSYSTEMS,TRAN,TYPE -d -J"
        try:
            stdin, stdout, stderr = ssh.ssh_execute(ssh_session=ssh_session, command=command)
        except Exception as e:
            return e

        response = stdout.read()
        res = response.decode('utf-8')

        stdin.close()
        stdout.close()
        stderr.close()

        return json.loads(res, encoding='utf-8')

    def fileno(self, file_or_fd):
        fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
        if not isinstance(fd, int):
            raise ValueError("Expected a file ('.fileno()') or a file descriptor")
        return fd

    @contextmanager
    def stdout_redirected(self, channel, stdout=None):
        channel.shutdown_write()
        stdout.write(channel.recv(len))
        with open(stdout, 'wb') as copied:
            copied.flush()
            try:
                copied.write(to.read())
            except ValueError:
                print("COPY FAILED")
        #print("stdout_fd {} {}".format(stdout, self.fileno(to)))
        #stdout_fd = self.fileno(stdout)
        #print("stdout_fd {} {}".format(stdout, stdout_fd))
        # with os.fdopen(os.dup(stdout_fd), 'wb') as copied:
        #     stdout.flush()
        #     try:
        #         os.dup2(self.fileno(to), stdout_fd)
        #     except ValueError:
        #         with open(to, 'wb') as to_file:
        #             os.dup2(to_file.fileno(), stdout_fd)
        #
        #     try:
        #         yield stdout
        #     finally:
        #         stdout.flush()
        #         os.dup2(copied.fileno(), stdout_fd)

    @Base.ssh_connect
    def dev_part_dump(self, dev_name, dump_path, remote_server=None, ssh=None, ssh_session=None):

        # fdisk -d /dev/sda

        dev_path = "/dev/{}".format(dev_name)
        command = "sfdisk -d \"{}\"".format(dev_path)
        try:
            stdin, stdout, stderr = ssh.ssh_execute(ssh_session=ssh_session, command=command)
        except Exception as e:
            print("error execute")
            return e

        response = stdout.read()
        res = response.decode('utf-8')
        print(res)
        with open(dump_path, 'w') as fdout:
            fdout.write(res)
        # print(res)
        # timeout = 5
        channel = stdout.channel
        # channel.shutdown_write()
        stdin.close()

        # with open(dump_path, 'wb') as fdout:
        #     fdout.write(channel.recv(len(channel.in_buffer)))
        #     while not channel.closed:
        #         readq, _, _ = select.select([channel],[],[],timeout)
        #         for c in readq:
        #             if c.recv_ready():
        #                 fdout.write(channel.recv(len(channel.in_buffer)))
        #             if c.recv_stderr_ready():
        #                 fdout.write(channel.recv(len(channel.in_buffer)))
        #         if channel.exit_status_ready() and not channel.recv_stderr_ready() and not channel.recv_ready():
        #             channel.shutdown_read()
        #             channel.close()
        #             break


        stdout.close()
        stderr.close()

        return channel.recv_exit_status()



