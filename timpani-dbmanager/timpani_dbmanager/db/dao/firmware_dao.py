import logging
from .base_dao import BaseDAO
from ..models.firmware import FirmwareDepandency, FirmwareDepandencyHW, FirmwareHist, FirmwareImage
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

# class FirmwareImage(Base):
#     __tablename__ = "tb_firmware_image"
#
#     id = Column("id", Integer, primary_key=True)
#     bios_id = Column(Integer, ForeignKey('tb_bios.id'))
#     fw_file_name = Column(String(128), nullable=True)
#     fw_file_path = Column(String(256), nullable=True)
#     fw_type = Column(String(32), nullable=True)
#     fw_type_code = Column(String(32), nullable=True)
#     fw_version = Column(String(64), nullable=True)
#     product_name = Column(String(256), nullable=True)
#     product_code = Column(String(64), nullable=True)
#     vendor = Column(String(64), nullable=True)
#     release_day = Column(String(32), nullable=True)
#     package_kind = Column(String(32), nullable=True)
#     package_kind_code = Column(String(32), nullable=True)
#     register_dt = Column(DateTime(timezone=True), default=func.now())
class FirmwareImageDAO(BaseDAO):
    @staticmethod
    def register_firmwareimage(data, database_session):
        # list = database_session.query(FirmwareImage).filter(
        #     FirmwareImage.image_id == data.get('image_id')).all()
        # logger.info("list size : {} === {}".format(len(list), list))
        # if len(list) != 0:
        #     return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = FirmwareImage()
        field_list = ["bios_id", "fw_file_name", "fw_file_path", "fw_type", "fw_type_code", "fw_version", "product_name", "product_code", "vendor", "release_day", "package_kind_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def update_firmwareimage(data, database_session):
        obj = database_session.query(FirmwareImage).filter(
            FirmwareImage.bios_id == data.get('bios_id')).first()
        field_list = ["bios_id", "fw_file_name", "fw_file_path", "fw_type", "fw_type_code", "fw_version",
                      "product_name", "product_code", "vendor", "release_day", "package_kind_code"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def del_firmwareimage(data, database_session):
        try:
            data = database_session.query(FirmwareImage).filter(
                FirmwareImage.image_id == data.get('image_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

# class FirmwareDepandency(Base):
#     __tablename__ = "tb_firmware_depandency"
#
#     id = Column("id", Integer, primary_key=True)
#     image_id = Column(Integer, ForeignKey('tb_firmware_image.id'))
#
#     fw_type = Column(String(32), nullable=True)
#     fw_type_code = Column(String(32), nullable=True)
#     fw_version = Column(String(64), nullable=True)
#     register_dt = Column(DateTime(timezone=True), default=func.now())
class FirmwareDepandencyDAO(BaseDAO):
    @staticmethod
    def register_firmwaredepandency(data, database_session):
        list = database_session.query(FirmwareDepandency).filter(
            FirmwareDepandency.image_id == data.get('image_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = FirmwareDepandency()
        field_list = ["image_id", "fw_type", "fw_type_code", "fw_version"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def update_pxeboot(data, database_session):
        obj = database_session.query(FirmwareDepandency).filter(
            FirmwareDepandency.image_id == data.get('image_id')).first()
        field_list = ["image_id", "fw_type", "fw_type_code", "fw_version"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def del_pxeboot(data, database_session):
        try:
            data = database_session.query(FirmwareDepandency).filter(
                FirmwareDepandency.image_id == data.get('image_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

# class FirmwareDepandencyHW(Base):
#     __tablename__ = "tb_firmware_depandency_hw"
#
#     id = Column("id", Integer, primary_key=True)
#     image_id = Column(Integer, ForeignKey('tb_firmware_image.id'))
#     product_name = Column(String(256), nullable=True)
#     product_code = Column(String(64), nullable=True)
#     vendor = Column(String(64), nullable=True)
#     register_dt = Column(DateTime(timezone=True), default=func.now())
class FirmwareDepandencyHWDAO(BaseDAO):
    @staticmethod
    def register_firmwaredepandencyhw(data, database_session):
        list = database_session.query(FirmwareDepandencyHW).filter(
            FirmwareDepandencyHW.image_id == data.get('image_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = FirmwareDepandencyHW()
        field_list = ["image_id", "product_name", "product_code", "vendor"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def update_firmwaredepandencyhw(data, database_session):
        obj = database_session.query(FirmwareDepandencyHW).filter(
            FirmwareDepandencyHW.image_id == data.get('image_id')).first()
        field_list = ["image_id", "product_name", "product_code", "vendor"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.image_id

    @staticmethod  # @BaseDAO.database_operation
    def del_firmwaredepandencyhw(data, database_session):
        try:
            data = database_session.query(FirmwareDepandencyHW).filter(
                FirmwareDepandencyHW.image_id == data.get('image_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

# class FirmwareHist(Base):
#     __tablename__ = "tb_firmware_hist"
#
#     id = Column("id", Integer, primary_key=True)
#     node_uuid = Column(CHAR(32), ForeignKey('tb_node.uuid'))
#     fw_type = Column(String(32), nullable=True)
#     fw_type_code = Column(String(32), nullable=True)
#     fw_version = Column(String(64), nullable=True)
#     product_name = Column(String(256), nullable=True)
#     product_code = Column(String(64), nullable=True)
#     vendor = Column(String(64), nullable=True)
#     release_day = Column(String(32), nullable=True)
#     package_kind = Column(String(32), nullable=True)
#     package_kind_code = Column(String(32), nullable=True)
#     action = Column(String(64))
#     action_code = Column(String(32))
#     result = Column(String(32))
#     result_code = Column(String(32))
#     error = Column(String(256))
#     error_code = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())

class FirmwareHistDAO(BaseDAO):
    @staticmethod
    def register_firmwarehist(data, database_session):
        list = database_session.query(FirmwareHist).filter(
            FirmwareHist.node_uuid == data.get('node_uuid')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = FirmwareHist()
        field_list = ["node_uuid", "fw_type", "fw_type_code", "fw_version", "product_name", "product_code", "release_day","vendor", "package_kind", "package_kind_code", "action", "action_code", "result", "result_code", "error", "error_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_firmwarehist(data, database_session):
        obj = database_session.query(FirmwareHist).filter(
            FirmwareHist.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "fw_type", "fw_type_code", "fw_version", "product_name", "product_code",
                      "release_day", "vendor", "package_kind", "package_kind_code", "action", "action_code", "result",
                      "result_code", "error", "error_code"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_firmwarehist(data, database_session):
        try:
            data = database_session.query(FirmwareHist).filter(
                FirmwareHist.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'