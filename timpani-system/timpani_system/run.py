import re
from timpani_system.zfs import ZFS
from timpani_system.resource import ResourceSystem
from timpani_system.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_system.configuration.config_set import ConfigSetting
import datetime
from multiprocessing import Queue

import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.DEBUG)
logger.addHandler(stream_hander)
#######################################################################################################################


def getNowStr(node_name:str):
    now = datetime.datetime.now()
    nowDate = now.strftime('%Y%m%d%H%M%S')
    res = node_name + "-" + nowDate
    return nowDate

def testSnapshot():
    logger.info("TEST SnapShot")

def metadatacollection():
    res_data = {}
    # partition information collecation

    # zpool property collection
    zpool_property = ResourceSystem.getZpoolGetAll()

    # zfs property collection
    zfs_property = ResourceSystem.getZfsGetAll()

    # zfs list -Hv
    zpool_status = ResourceSystem.zpoollistHv()
    print(zpool_status)

    # geom list
    # geom_list = ResourceSystem.geomlist()
    zdb_list = ResourceSystem.zdb_list()
    res_data = {'zpool_property': zpool_property, 'zfs_property': zfs_property, 'zdb_list': zdb_list}
    print("res_data : {}".format(res_data))
    return res_data


def test():
    logger.info("TEST")
    snapshot_list, dataset_list, snapname_list = ResourceSystem.getSnapShotList()
    logger.info("snapshot_list : {}".format(snapshot_list))
    logger.info("dataset_list : {}".format(dataset_list))
    logger.info("snapname_list : {}".format(snapname_list))
    # All Snapshot Destory
    for snapname in snapshot_list:
        ResourceSystem.FullDestorySnapshot(snapname)

    # Get Zpool list data
    zpool_list = ResourceSystem.getZpoolList()
    logger.info("zpool list : {}".format(zpool_list))

    now_date = getNowStr("test")
    snapname = "F-{}".format(now_date)
    send_list = []
    for pool in zpool_list:
        # Checksum Test File Create
        zfs_list = ResourceSystem.getZfsList(target=pool, recursive=True)
        logger.info("zfs list : {}".format(zfs_list))
        for dataset, mountpoint in zfs_list:
            checksum_list = ResourceSystem.timpani_checksum(dataset=dataset, mountpoint=mountpoint)
            logger.info("checksum_lsit : {}".format(checksum_list))

        # Create Snapshot
        create_list = ResourceSystem.FullSnapshot(poolname=pool, snapname=snapname)
        check_snapshot_str = "{}@{}".format(pool, snapname)
        for snapshot_name in create_list:
            if snapshot_name.__eq__(check_snapshot_str):
                send_list.append(snapshot_name)

    logger.info("send list : {}".format(send_list))

    for send_target in send_list:
        remote_path = '/opt/timpani/{}'.format(send_target)
        res = ResourceSystem.FullBackupSend(send_target=send_target, target_host='backup-server', remote_path=remote_path)

from timpani_system.action import Action

def test_1():
    master_q = Queue()
    action = Action(master_q)
    action.start()
    action.FullBackup()
    while True:
        msg = master_q.get()
        print("Master Queue : {}".format(msg))
        if msg.get('action').__eq__('END'):
            action.end()
            break

def test_2():
    res = ResourceSystem.GetBackupSrcList()
    print(res)

import click
import yaml

@click.command()
@click.argument('command')
def main(command):
    print("TEST main")

    if command.__eq__('test_snapshot'):
        testSnapshot()
    elif command.__eq__('test'):
        test_2()


if __name__ == "__main__":
    main()

#     config = ConfigrationFileReader()
#     config_set = ConfigSetting(config.read_file())
#     config_set.setConfig()
#
#     print(ResourceSystem.getSystemZfsList())
#
#     isIncrement = False                 # Incremental Backup : True , Full Backup : False
#     src_target = "array1"
#     now_date = getNowStr("test")
#
#     # ZFS Get All property
#     print(ZFS.zfs_get(target=src_target))
#     ResourceSystem.getZpoolGetAll()
#     ResourceSystem.getZfsGetAll()
#
#     res = ResourceSystem.getBaseInformation()
#     print(res)
#
#     if isIncrement:
#         snapname = "I{}".format(now_date)
#     else:
#         snapname = "F{}".format(now_date)

    # # create snapshot
    # ZFS.zfs_snapshot(filesystem=src_target, snapname=snapname)
    # # get snapshot file
    # ZFS.zfs_send(filesystem=src_target, snapname=snapname)
    #
    # snapshot_nm = "{}@{}".format(src_target, snapname)



# class System(Base):
#     __tablename__ = "tb_system"
#
#     id = Column(Integer, primary_key=True)
#     node_uuid = Column(CHAR(32), ForeignKey('tb_node.uuid'))
#     #node = relationship("Node", back_populates="system")
#     meta_id = Column(Integer, ForeignKey('tb_system_backup_meta.id'))
#     # backupmeta = relationship("SystemBackupMeta", back_populates="system")
#     # Agent Collection Information
#     ipv4address = Column(String(64))
#     os_type = Column(String(32))
#     os_type_code = Column(String(32))
#     os_version = Column(String(32))
#     os_arch = Column(String(32))
#     os_arch_code = Column(String(32))
#     kernel_version = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
# class SystemZfs(Base):
#     __tablename__ = "tb_system_zfs"
#
#     id = Column(Integer, primary_key=True)
#     system_id = Column(Integer, ForeignKey('tb_system.id'))
#     zfs_used_size = Column(String(64))
#     zfs_avail_size = Column(String(64))
#     zfs_mount_point = Column(String(256))
#     zfs_name = Column(String(256))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#
# class SystemDisk(Base):
#     __tablename__ = "tb_system_disk"
#
#     id = Column(Integer, primary_key=True)
#     system_id = Column(Integer, ForeignKey('tb_system.id'))
#     disk_used = Column(String(64))
#     disk_free = Column(String(64))
#     disk_avail = Column(String(64))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
