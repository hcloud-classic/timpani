import logging
from .base_dao import BaseDAO
from ..models.pxeboot import Pxeboot, PxebootImage, PxebootHist
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

# class PxebootImage(Base):
#     __tablename__ = "tb_pxeboot_image"
#
#     id = Column(Integer, primary_key=True)
#     os_type = Column(String(32))
#     os_type_code = Column(String(32))
#     os_version = Column(String(32))
#     os_arch = Column(String(32))
#     os_arch_code = Column(String(32))
#     label = Column(String(128))
#     repo_name = Column(String(256))
#     vmlinuz_path = Column(String(256))
#     initrd_path = Column(String(256))
#     image_file_path = Column(String(256))
#     image_file_name= Column(String(256))
#     target = Column(String(32))
#     target_code = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#

class PxebootImageDAO(BaseDAO):
    @staticmethod
    def register_pxebootimage(data, database_session):
        # list = database_session.query(PxebootImage).filter(
        #     PxebootImage.node_uuid == data.get('node_uuid')).all()
        # logger.info("list size : {} === {}".format(len(list), list))
        # if len(list) != 0:
        #     return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = PxebootImage()
        field_list = ["os_type", "os_type_code", "os_version", "os_arch", "os_arch_code", "label", "repo_name", "vmlinuz_path", "initrd_path", "image_file_path", "image_file_name", "target", "target_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_pxebootimage(data, database_session):
        obj = database_session.query(PxebootImage).filter(
            PxebootImage.node_uuid == data.get('node_uuid')).first()
        field_list = ["os_type", "os_type_code", "os_version", "os_arch", "os_arch_code", "label", "repo_name",
                      "vmlinuz_path", "initrd_path", "image_file_path", "image_file_name", "target", "target_code"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_pxebootimage(data, database_session):
        try:
            data = database_session.query(PxebootImage).filter(
                PxebootImage.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

# class Pxeboot(Base):
#     __tablename__ = "tb_pxeboot"
#
#     id = Column(Integer, primary_key=True)
#     ismount = Column(Integer, default=0)        # 0: not mounted 1: mounted
#     isdefault = Column(Integer, default=0)      # 0: no default  1: default
#     mount_path = Column(String(256), nullable=True)    # image mount path
#     image_id = Column(Integer,ForeignKey("tb_pxeboot_image.id"))
#

class PxebootDAO(BaseDAO):
    @staticmethod
    def register_pxeboot(data, database_session):
        list = database_session.query(Pxeboot).filter(
            Pxeboot.image_id == data.get('image_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = Pxeboot()
        field_list = ["ismount", "isdefault", "mount_path", "image_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def update_pxeboot(data, database_session):
        obj = database_session.query(Pxeboot).filter(
            Pxeboot.image_id == data.get('image_id')).first()
        field_list = ["ismount", "isdefault", "mount_path", "image_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def del_pxeboot(data, database_session):
        try:
            data = database_session.query(Pxeboot).filter(
                Pxeboot.image_id == data.get('image_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'


# class PxebootHist(Base):
#     __tablename__ = "tb_pxeboot_hist"
#
#     id = Column(Integer, primary_key=True)
#     os_type = Column(String(32))
#     os_type_code = Column(String(32))
#     os_version = Column(String(32))
#     os_arch = Column(String(32))
#     os_arch_code = Column(String(32))
#     label = Column(String(128))
#     target = Column(String(32))
#     target_code = Column(String(32))
#     action = Column(String(64))
#     action_code = Column(String(32))
#     result = Column(String(32))
#     result_code = Column(String(32))
#     error = Column(String(256))
#     error_code = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())

class PxebootHistDAO(BaseDAO):
    @staticmethod
    def register_pxeboothist(data, database_session):
        # list = database_session.query(PxebootHist).filter(
        #     PxebootHist.node_uuid == data.get('node_uuid')).all()
        # logger.info("list size : {} === {}".format(len(list), list))
        # if len(list) != 0:
        #     return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = PxebootHist()
        field_list = ["os_type", "os_type_code", "os_version", "os_arch", "os_arch_code", "label", "target", "target_code", "action", "action_code", "result", "result_code", "error", "error_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def update_pxeboothist(data, database_session):
        obj = database_session.query(PxebootHist).filter(
            PxebootHist.node_uuid == data.get('node_uuid')).first()
        field_list = ["os_type", "os_type_code", "os_version", "os_arch", "os_arch_code", "label", "target",
                      "target_code", "action", "action_code", "result", "result_code", "error", "error_code"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_pxeboothist(data, database_session):
        try:
            data = database_session.query(PxebootHist).filter(
                PxebootHist.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
