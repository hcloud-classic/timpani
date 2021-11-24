from timpani_base.net.openssh_command import SSHCommand
from timpani_base.exceptions.exception import SSHCommandException
from timpani_base.module.partition_info import PartitionInfo
import json

def test():
    p_info = PartitionInfo()
    #res = PartitionInfo.lsblk_dev_list(remote_server="192.168.221.215")
    res = p_info.lsblk_dev_list(remote_server="192.168.221.217")
    print(res)
    res = p_info.dev_part_dump(dev_name='sda', dump_path='./test', remote_server="192.168.221.217")
    print(res)

#ssh = SSHCommand()
#ssh_session  = ssh.connetion(server='192.168.221.215')
#if ssh_session is None:
#   print("ssh session None")
#try:
#   stdin, stdout, stderr = ssh.ssh_execute(ssh_session=ssh_session,command='ls -alh')
#except SSHCommandException as e:
#   print(e)

#for line in stdout.read().splitlines():
#   print(line)

#ssh.disconnetion(ssh_session)

if __name__=='__main__':
    test()
