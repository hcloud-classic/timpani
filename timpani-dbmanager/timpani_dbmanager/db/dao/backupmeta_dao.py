import logging
import datetime
from .base_dao import BaseDAO
from ..models.backupmeta import (MetaPool, MetaData, MetaDataRollback, MetaDeviceTree, IscsiInfo,
                                 MetaPoolProperty, MetaTargetProperty, SnapData, BootData)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

class MetaDataDAO(BaseDAO):

    FIELD = ['uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'snapname', 'pool_property_id',
             'zfs_property_id', 'pool_data_id', 'snapshot_data_id', 'boot_data_id', 'iscsiinfo_sub_id',
             'islast', 'isfull', 'ispolicebackup', 'register_dt'
            ]
    @staticmethod
    def addmetadata(data, database_session):
        field_list = MetaDataDAO.FIELD
        logger.info("[MeataDataDAO.addmetadata] data : {}".format(data))
        obj = MetaData()
        BaseDAO.set_value(obj, field_list, data)
        if obj.register_dt is not None:
            dt = datetime.datetime.strptime(obj.register_dt, '%Y-%m-%d %H:%M:%S')
            obj.register_dt = dt
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getlastdata(data, database_session):
        FIELD = ['id','pool_property_id', 'zfs_property_id', 'pool_data_id', 'snapshot_data_id', 'iscsiinfo_sub_id', 'snapname']
        query = database_session.query(MetaData.id, MetaData.pool_property_id,
                                       MetaData.zfs_property_id, MetaData.pool_data_id,
                                       MetaData.snapshot_data_id, MetaData.iscsiinfo_sub_id, MetaData.snapname)
        query = query.filter(MetaData.name == data.get('name'))
        query = query.filter(MetaData.nodetype == data.get('nodetype'))
        query = query.filter(MetaData.usetype == data.get('usetype'))
        query = query.filter(MetaData.islast == 1).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def getsnapshotdata(data, islast, database_session):
        FIELD = ['id', 'name', 'snapname', 'nodetype', 'usetype',
                 'uuid', 'target_uuid', 'islast', 'isfull', 'ispolicebackup',
                 'pool_property_id', 'zfs_property_id', 'iscsiinfo_sub_id', 'pool_data_id', 'snapshot_data_id', 'boot_data_id',
                 'register_dt', 'priv_snapname']
        query = database_session.query(MetaData.id,
                                       MetaData.name, MetaData.snapname, MetaData.nodetype, MetaData.usetype,
                                       MetaData.uuid, MetaData.target_uuid, MetaData.islast,
                                       MetaData.isfull, MetaData.ispolicebackup,
                                       MetaData.pool_property_id,
                                       MetaData.zfs_property_id,
                                       MetaData.iscsiinfo_sub_id,
                                       MetaData.pool_data_id,
                                       MetaData.snapshot_data_id, MetaData.boot_data_id,
                                       MetaData.register_dt,
                                       SnapData.priv_snapfullname)
        query = query.join(SnapData, SnapData.id == MetaData.snapshot_data_id)
        query = query.filter(MetaData.name == data.get('name'))
        query = query.filter(MetaData.nodetype == data.get('nodetype'))
        query = query.filter(MetaData.usetype == data.get('usetype'))
        if islast:
            query = query.filter(MetaData.islast == 1).first()
        else:
            query = query.order_by(MetaData.register_dt.asc())
            BaseDAO.debug_sql_print(query, "getsnapshotdata")
            query = query.all()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def getrestorelist(data, database_session):
        usetype = data.get("usetype").upper()
        authtype = data.get("authtype").upper()
        FIELD = ['name', 'snapname', 'nodetype', 'usetype',
                 'target_uuid', 'islast', 'isfull',
                 'snapfilename',
                 'time']
        query = database_session.query(MetaData.name, MetaData.snapname, MetaData.nodetype, MetaData.usetype,
                                       MetaData.target_uuid, MetaData.islast,
                                       MetaData.isfull, SnapData.snapfilename,
                                       MetaData.register_dt)
        query = query.join(SnapData, SnapData.id == MetaData.snapshot_data_id)
        if usetype.__eq__("ALL"):
            if authtype.__eq__("MASTER"):
                usetype_list = ["OS", "DATA", "ORIGIN"]
            elif authtype.__eq__("ADMIN"):
                usetype_list = ["OS", "DATA"]
            elif authtype.__eq__("USER"):
                usetype_list = ["DATA"]
            query = query.filter(MetaData.usetype.in_(usetype_list))
        else:
            query = query.filter(MetaData.usetype == usetype)

        if 'namelist' in data:
            namelist = data.get('namelist')
            if not authtype.__eq__("MASTER"):
                query = query.filter(MetaData.name.in_(namelist))

        query = query.order_by(MetaData.register_dt.desc())
        BaseDAO.debug_sql_print(query, "getrestorelist")
        query = query.all()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD, ins_field='isrollback', ins_val='N')
        else:
            return None
        return res

    @staticmethod
    def getrestoresnapdata(data, database_session):
        FIELD = ['id', 'server_uuid', 'target_uuid', 'name', 'pool_property_id',
                 'zfs_property_id', 'pool_data_id', 'snapshot_data_id', 'iscsiinfo_sub_id', 'boot_data_id']
        query = database_session.query(MetaData.id, MetaData.uuid, MetaData.target_uuid,
                                       MetaData.name, MetaData.pool_property_id,
                                       MetaData.zfs_property_id, MetaData.pool_data_id,
                                       MetaData.snapshot_data_id, MetaData.iscsiinfo_sub_id,
                                       MetaData.boot_data_id)
        query = query.filter(MetaData.snapname == data.get('snapname'))
        query = query.filter(MetaData.nodetype == data.get('nodetype'))
        query = query.filter(MetaData.usetype == data.get('usetype')).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def delonesnap(data, database_session):
        FIELD = ['id', 'snapname', 'server_uuid', 'target_uuid', 'priv_filename', 'filename', 'save_path', 'part_path']
        snapname = data.get('snapname')
        query = database_session.query(MetaData.id,
                                       MetaData.snapname,
                                       MetaData.uuid,
                                       MetaData.target_uuid,
                                       SnapData.priv_snapfilename,
                                       SnapData.snapfilename,
                                       SnapData.save_path,
                                       SnapData.part_path
                                       )
        query = query.join(SnapData, SnapData.snapname == MetaData.snapname)
        query = query.filter(MetaData.snapname == snapname).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def dellastsnap(data, database_session):
        FIELD = ['id', 'snapname', 'server_uuid', 'target_uuid', 'priv_filename', 'filename', 'save_path', 'part_path']
        snapname = data.get('snapname')
        query = database_session.query(MetaData.id,
                                       MetaData.snapname,
                                       MetaData.uuid,
                                       MetaData.target_uuid,
                                       SnapData.priv_snapfilename,
                                       SnapData.snapfilename,
                                       SnapData.save_path,
                                       SnapData.part_path
                                       )
        query = query.join(SnapData, SnapData.snapname == MetaData.snapname)
        query = query.filter(MetaData.snapname == snapname)
        query = query.filter(MetaData.islast == 1).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def issnapname(data, database_session):
        query = database_session.query(MetaData).filter(MetaData.snapname == data.get('snapname')).first()

        if query is not None:
            logger.info("[MetaData] query Not None : issnapname :{} ".format(data.get('snapname')))
            return True
        else:
            logger.info("[MetaData] query None : issnapname :{} ".format(data.get('snapname')))
            return False

    @staticmethod
    def privlastflagchange(priv_id, database_session):
        obj = database_session.query(MetaData).filter(MetaData.id == priv_id).first()
        if obj is None:
            return False
        obj.islast = 0
        BaseDAO.update(obj, database_session)

        return True

    @staticmethod
    def setlastflag(snapname, database_session):
        obj = database_session.query(MetaData).filter(MetaData.snapname == snapname).first()
        if obj is None:
            return False
        obj.islast = 1
        BaseDAO.update(obj, database_session)

        return True

    @staticmethod
    def setlastflagoff(snapname, database_session):
        obj = database_session.query(MetaData).filter(MetaData.snapname == snapname).first()
        if obj is None:
            return False
        obj.islast = 0
        BaseDAO.update(obj, database_session)

        return True

    @staticmethod
    def setlastflagoff_id(set_id, database_session):
        obj = database_session.query(MetaData).filter(MetaData.id == set_id).first()
        if obj is None:
            return False
        obj.islast = 0
        BaseDAO.update(obj, database_session)

        return True

    @staticmethod
    def snapdel_setlastflag(snapname, database_session):
        query = database_session.query(MetaData.id, MetaData.islast, SnapData.priv_snapfilename).join(SnapData, SnapData.id == MetaData.snapshot_data_id)
        query = query.filter(MetaData.snapname == snapname).first()
        if query is None:
            return False

        temp_data = list(query)
        if temp_data[1] == 1 and temp_data[2] is not None:
            obj = database_session.query(MetaData).join(SnapData, SnapData.id == MetaData.snapshot_data_id)
            obj = obj.filter(SnapData.snapfilename == temp_data[2]).first()
            obj.islast = 1
            BaseDAO.update(obj, database_session)

        del_obj = database_session.query(MetaData).filter(MetaData.snapname == snapname).first()
        BaseDAO.delete(del_obj, database_session)
        return True

    @staticmethod
    def privdatadel(snapname, database_session):
        obj = database_session.query(MetaData).filter(MetaData.snapname == snapname).first()
        if obj is None:
            logger.info("privdatadel[MetaDATA] Delete FAILED {}".format(snapname))
            return False
        BaseDAO.delete(obj, database_session)
        return True



class MetaDataRollbackDAO(BaseDAO):
    FIELD = ['meta_id', 'uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'snapname', 'pool_property_id',
             'zfs_property_id', 'pool_data_id', 'snapshot_data_id', 'boot_data_id', 'iscsiinfo_sub_id',
             'islast', 'isfull', 'ispolicebackup', 'register_dt'
             ]

    @staticmethod
    def addmetadata(data, database_session):
        field_list = MetaDataRollbackDAO.FIELD
        if 'name' in data:
            name = data.get('name')

        snapname = data.get('snapname')

        query = database_session.query(MetaDataRollback)
        query = query.filter(MetaDataRollback.snapname == snapname).first()
        if query is None:
            obj = MetaDataRollback()
            BaseDAO.set_value(obj, field_list, data)
            dt = datetime.datetime.strptime(obj.register_dt, '%Y-%m-%d %H:%M:%S')
            obj.register_dt = dt
            BaseDAO.insert(obj, database_session)
            return obj.id
        else:
            logger.info("addmetadata[MetaRollback] ADD FAILED {}".snapname)
            return -1


    @staticmethod
    def getsnapshotdata(data, islast, database_session):
        FIELD = ['id', 'name', 'snapname', 'nodetype', 'usetype',
                 'uuid', 'target_uuid', 'islast', 'isfull', 'ispolicebackup',
                 'pool_property_id', 'zfs_property_id', 'pool_data_id', 'snapshot_data_id',
                 'boot_data_id', 'iscsiinfo_sub_id',
                 'register_dt','priv_snapname']
        query = database_session.query(MetaDataRollback.meta_id,
                                       MetaDataRollback.name, MetaDataRollback.snapname,
                                       MetaDataRollback.nodetype, MetaDataRollback.usetype,
                                       MetaDataRollback.uuid, MetaDataRollback.target_uuid, MetaDataRollback.islast,
                                       MetaDataRollback.isfull, MetaDataRollback.ispolicebackup,
                                       MetaDataRollback.pool_property_id,
                                       MetaDataRollback.zfs_property_id, MetaDataRollback.pool_data_id,
                                       MetaDataRollback.snapshot_data_id, MetaDataRollback.boot_data_id,
                                       MetaDataRollback.iscsiinfo_sub_id,
                                       MetaDataRollback.register_dt,
                                       SnapData.priv_snapfullname)
        query = query.join(SnapData, SnapData.id == MetaDataRollback.snapshot_data_id)
        query = query.filter(MetaDataRollback.name == data.get('name'))
        query = query.filter(MetaDataRollback.nodetype == data.get('nodetype'))
        query = query.filter(MetaDataRollback.usetype == data.get('usetype'))
        if islast:
            query = query.filter(MetaDataRollback.islast == 1).first()
        else:
            query = query.order_by(MetaDataRollback.meta_id.asc())
            BaseDAO.debug_sql_print(query, "getsnapshotdata")
            query = query.all()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def getrestoresnapdata(data, database_session):
        FIELD = ['id', 'server_uuid', 'target_uuid', 'name', 'pool_property_id', 'zfs_property_id', 'pool_data_id',
                 'snapshot_data_id', 'iscsiinfo_sub_id', 'boot_data_id']
        query = database_session.query(MetaDataRollback.meta_id, MetaDataRollback.uuid, MetaDataRollback.target_uuid,
                                       MetaDataRollback.name, MetaDataRollback.pool_property_id,
                                       MetaDataRollback.zfs_property_id, MetaDataRollback.pool_data_id,
                                       MetaDataRollback.snapshot_data_id,
                                       MetaDataRollback.iscsiinfo_sub_id,
                                       MetaDataRollback.boot_data_id)
        query = query.filter(MetaDataRollback.snapname == data.get('snapname'))
        query = query.filter(MetaDataRollback.nodetype == data.get('nodetype'))
        query = query.filter(MetaDataRollback.usetype == data.get('usetype')).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def delonesnap(data, database_session):
        FIELD = ['id', 'snapname', 'server_uuid', 'target_uuid', 'priv_filename', 'filename', 'save_path', 'part_path']
        snapname = data.get('snapname')
        query = database_session.query(MetaDataRollback.id,
                                       MetaDataRollback.snapname,
                                       MetaDataRollback.uuid,
                                       MetaDataRollback.target_uuid,
                                       SnapData.priv_snapfilename,
                                       SnapData.snapfilename,
                                       SnapData.save_path,
                                       SnapData.part_path
                                       )
        query = query.join(SnapData, SnapData.snapname == MetaDataRollback.snapname)
        query = query.filter(MetaDataRollback.snapname == snapname).first()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def delmanysnap(data, database_session):
        FIELD = ['id', 'snapname', 'server_uuid', 'target_uuid', 'priv_filename', 'filename', 'save_path', 'part_path']

        query = database_session.query(MetaDataRollback.id,
                                       MetaDataRollback.snapname,
                                       MetaDataRollback.uuid,
                                       MetaDataRollback.target_uuid,
                                       SnapData.priv_snapfilename,
                                       SnapData.snapfilename,
                                       SnapData.save_path,
                                       SnapData.part_path
                                       )
        query = query.join(SnapData, SnapData.id == MetaDataRollback.snapshot_data_id)
        if 'usetype' in data:
            if data.get('usetype') is not None:
                query = query.filter(MetaDataRollback.usetype == data.get('usetype'))

        if 'nodetype' in data:
            if data.get('nodetype') is not None:
                query = query.filter(MetaDataRollback.nodetype == data.get('nodetype'))
        query = query.all()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return None
        return res

    @staticmethod
    def getrestorelist(data, database_session):
        usetype = data.get("usetype").upper()
        authtype = data.get("authtype").upper()
        FIELD = ['name', 'snapname', 'nodetype', 'usetype',
                 'target_uuid', 'islast', 'isfull',
                 'snapfilename',
                 'time']
        query = database_session.query(MetaDataRollback.name, MetaDataRollback.snapname,
                                       MetaDataRollback.nodetype, MetaDataRollback.usetype,
                                       MetaDataRollback.target_uuid, MetaDataRollback.islast,
                                       MetaDataRollback.isfull, SnapData.snapfilename,
                                       MetaDataRollback.register_dt)
        query = query.join(SnapData, SnapData.id == MetaDataRollback.snapshot_data_id)
        if usetype.__eq__("ALL"):
            if authtype.__eq__("MASTER"):
                usetype_list = ["OS", "DATA", "ORIGIN"]
            elif authtype.__eq__("ADMIN"):
                usetype_list = ["OS", "DATA"]
            elif authtype.__eq__("USER"):
                usetype_list = ["DATA"]
            query = query.filter(MetaDataRollback.usetype.in_(usetype_list))
        else:
            query = query.filter(MetaDataRollback.usetype == usetype)

        if 'namelist' in data:
            namelist = data.get('namelist')
            if not authtype.__eq__("MASTER"):
                query = query.filter(MetaDataRollback.name.in_(namelist))

        query = query.order_by(MetaDataRollback.register_dt.desc())
        BaseDAO.debug_sql_print(query, "getrestorelist")
        query = query.all()

        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD, ins_field='isrollback', ins_val='Y')
        else:
            return None
        return res

    @staticmethod
    def issnapname(data, database_session):
        query = database_session.query(MetaDataRollback).filter(MetaDataRollback.snapname == data.get('snapname')).first()

        if query is not None:
            logger.info("[MetaDataRollBack] query Not None : issnapname :{} ".format(data.get('snapname')))
            return True
        else:
            logger.info("[MetaDataRollBack] query None : issnapname :{} ".format(data.get('snapname')))
            return False

    @staticmethod
    def privdatadel(data, database_session):
        query = database_session.query(MetaDataRollback)
        query = query.filter(MetaDataRollback.usetype == data.get('usetype'))
        query = query.filter(MetaDataRollback.nodetype == data.get('nodetype'))
        query = query.filter(MetaDataRollback.name == data.get('name'))
        BaseDAO.debug_sql_print(query, "privdatadel[Rollback]")
        query = query.all()
        # data['rollback_db_data'] = query
        if query is None:
            for obj in query:
                BaseDAO.delete(obj,database_session)
        return True

    @staticmethod
    def privdatadel(snapname, database_session):
        obj = database_session.query(MetaDataRollback).filter(MetaDataRollback.snapname == snapname).first()
        if obj is None:
            logger.info("privdatadel[MetaDATARollback] Delete FAILED {}".format(snapname))
            return False
        BaseDAO.delete(obj, database_session)
        return True





class MetaPoolDAO(BaseDAO):
    FIELD = ['sub_id', 'pool', 'ashift', 'create_option']

    @staticmethod
    def addmetapooldata(data, database_session):
        field_list = MetaPoolDAO.FIELD

        obj = MetaPool()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.sub_id

    @staticmethod
    def getprivdata(priv_id, database_session):
        query = database_session.query(MetaPool.sub_id, MetaPool.pool,
                                       MetaPool.ashift, MetaPool.create_option)
        query = query.filter(MetaPool.sub_id == priv_id).first()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=MetaPoolDAO.FIELD)

        return res



# class MetaDeviceTreeDAO(BaseDAO):
#     FIELD = ['uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'pool_property_id',
#              'zfs_property_id', 'pool_data_id', 'snapshot_data_id', '_id',
#              'islast'
#              ]
#
#     @staticmethod
#     def addmetadata(data, database_session):
#         field_list = MetaDataDAO.FIELD
#
#         obj = MetaData()
#         BaseDAO.set_value(obj, field_list, data)
#         BaseDAO.insert(obj, database_session)
#
#         return obj.id

class MetaPoolPropertyDAO(BaseDAO):     #ZPOOL Property

    FIELD = ['pool', 'sub_id', 'property', 'value', 'source']

    @staticmethod
    def addpoolproperty(data, database_session):
        field_list = MetaPoolPropertyDAO.FIELD

        obj = MetaPoolProperty()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.sub_id

    @staticmethod
    def getprivpropertylist(priv_id, database_session):
        query = database_session.query(MetaPoolProperty.pool, MetaPoolProperty.sub_id, MetaPoolProperty.property,
                                       MetaPoolProperty.value, MetaPoolProperty.source)
        query = query.filter(MetaPoolProperty.sub_id == priv_id).all()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=MetaPoolPropertyDAO.FIELD)

        return res

    # @staticmethod
    # def getpoolproperty(data, database_session):
    #     pool = data.get('propertys')
    #     query = database_session.query(MetaPoolProperty.pool, MetaPoolProperty.sub_id, MetaPoolProperty.property,
    #                                    MetaPoolProperty.value, MetaPoolProperty.source)
    #     query = query.filter(MetaPoolProperty.pool == data.get('pool'))
    # def check_property(data, database_session):

class MetaTargetPropertyDAO(BaseDAO):    #ZFS Property
    FIELD = ['pool', 'dataset', 'name', 'zfstype', 'sub_id', 'property', 'value',
             'source']

    @staticmethod
    def addzfsproperty(data, database_session):
        field_list = MetaTargetPropertyDAO.FIELD

        obj = MetaTargetProperty()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.sub_id

    def getprivpropertylist(priv_id, database_session):
        query = database_session.query(MetaTargetProperty.pool,
                                       MetaTargetProperty.dataset,
                                       MetaTargetProperty.name,
                                       MetaTargetProperty.zfstype,
                                       MetaTargetProperty.sub_id,
                                       MetaTargetProperty.property,
                                       MetaTargetProperty.value,
                                       MetaTargetProperty.source)
        query = query.filter(MetaTargetProperty.sub_id == priv_id).all()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=MetaTargetPropertyDAO.FIELD)

        return res

class SnapDataDAO(BaseDAO):    #snapshot file data
    FIELD = ['dataset', 'snapname', 'snapfilename', 'snapfullname', 'priv_snapfilename', 'priv_snapfullname',
             'save_path', 'part_path', 'isfull']

    @staticmethod
    def addsnapdata(data, database_session):
        field_list = SnapDataDAO.FIELD

        obj = SnapData()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getprivdata(priv_id, database_session):
        query = database_session.query(SnapData.dataset,
                                       SnapData.snapname,
                                       SnapData.snapfilename,
                                       SnapData.snapfullname,
                                       SnapData.priv_snapfilename,
                                       SnapData.priv_snapfullname,
                                       SnapData.save_path,
                                       SnapData.part_path,
                                       SnapData.isfull)
        query = query.filter(SnapData.id == priv_id).first()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=SnapDataDAO.FIELD)

        return res

class BootDataDAO(BaseDAO):    #snapshot file data
    FIELD = ['pool', 'path', 'devname']

    @staticmethod
    def addbootdata(data, database_session):
        field_list = BootDataDAO.FIELD

        obj = BootData()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getprivdata(priv_id, database_session):
        query = database_session.query(BootData.pool,
                                       BootData.path,
                                       BootData.devname,
                                       )
        query = query.filter(BootData.id == priv_id).first()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=BootDataDAO.FIELD)

        return res

class IscsiInfoDAO(BaseDAO):    #ZFS Property
    FIELD = ['sub_id', 'lun_id', 'backend_type', 'lun_type', 'size', 'blocksize', 'serial_number',
             'device_id', 'num_threads', 'file_path', 'ctld_name', 'scsiname', 'server_uuid',
             'target_uuid']

    @staticmethod
    def setdata(data, database_session):
        field_list = IscsiInfoDAO.FIELD

        obj = IscsiInfo()
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.sub_id

    @staticmethod
    def getsubid(data, database_session):
        query = database_session.query(IscsiInfo)
        query = query.order_by(IscsiInfo.sub_id.desc()).first()

        if query is None:
            return None

        return query.sub_id


    def getlist(sub_id, database_session):
        query = database_session.query(IscsiInfo.sub_id,
                                       IscsiInfo.lun_id,
                                       IscsiInfo.backend_type,
                                       IscsiInfo.lun_type,
                                       IscsiInfo.size,
                                       IscsiInfo.blocksize,
                                       IscsiInfo.serial_number,
                                       IscsiInfo.device_id,
                                       IscsiInfo.num_threads,
                                       IscsiInfo.file_path,
                                       IscsiInfo.ctld_name,
                                       IscsiInfo.scsiname,
                                       IscsiInfo.server_uuid,
                                       IscsiInfo.target_uuid)
        query = query.filter(IscsiInfo.sub_id == sub_id).all()
        if query is None:
            return None
        res = BaseDAO.return_data(query=query, field_list=IscsiInfoDAO.FIELD)

        return res


