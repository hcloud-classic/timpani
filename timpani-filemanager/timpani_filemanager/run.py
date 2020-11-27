from timpani_filemanager.filetrans import SSHManager

import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setLevel(level=logging.DEBUG)
stream_hander.setFormatter(formatter)
logger.addHandler(stream_hander)
#######################################################################################################################

def main():
    ssh_manager = SSHManager()
    logger.info("CREATE SSH CLIENT")
    ssh_manager.create_ssh_client(hostname='localhost', username='psh7511', password='qkrtjdgh')
    ssh_manager.send_command("ls -al")

if __name__=="__main__":
    main()