import logging
import datetime
from pytz import timezone
from timpani_dbmanager.db import dao
from .base import Base
from ..db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class MetaAPI(object):
    base = Base()

    def savepoolpropertydata(self, pool_property_id, zpool_property, zfs_property_id, zfs_property, database_session):
        issave = False
        pool_property_sub_id = pool_property_id
        zfs_property_sub_id = zfs_property_id
        if zfs_property_id > 0:
            privzfspropertys = dao.backupmeta_dao.MetaTargetPropertyDAO.getprivpropertylist(zfs_property_id,
                                                                                            database_session)
            equl_cnt = 0
            property_size = len(zfs_property)
            priv_property_size = len(privzfspropertys)
            if property_size == priv_property_size:
                for property in zfs_property:
                    k = property.get('property')
                    v = property.get('value')
                    s = property.get('source')
                    for priv_property in privzfspropertys:
                        priv_k = priv_property.get('property')
                        priv_v = priv_property.get('value')
                        priv_s = priv_property.get('source')
                        if k.__eq__(priv_k) and v.__eq__(priv_v) and s.__eq__(priv_s):
                            equl_cnt += 1

                    if equl_cnt != property_size:
                        issave = True

            else:
                issave = True
        else:
            if zfs_property_id == 0:
                issave = True

        if issave:
            # logger.info("zfs_property : {}".format(zfs_property))
            for property in zfs_property:
                property['sub_id'] = zfs_property_id + 1
                zfs_property_sub_id = dao.backupmeta_dao.MetaTargetPropertyDAO.addzfsproperty(property, database_session)

        if pool_property_id > 0:
            privpoolpropertys = dao.backupmeta_dao.MetaPoolPropertyDAO.getprivpropertylist(pool_property_id,
                                                                                           database_session)
            equl_cnt = 0
            property_size = len(zpool_property)
            priv_property_size = len(privpoolpropertys)
            if property_size == priv_property_size:
                for property in zpool_property:
                    k = property.get('property')
                    v = property.get('value')
                    s = property.get('source')
                    for priv_property in privpoolpropertys:
                        priv_k = priv_property.get('property')
                        priv_v = priv_property.get('value')
                        priv_s = priv_property.get('source')
                        if k.__eq__(priv_k) and v.__eq__(priv_v) and s.__eq__(priv_s):
                            equl_cnt += 1

                    if equl_cnt != property_size:
                        issave = True

            else:
                issave = True
        else:
            if pool_property_id == 0:
                issave = True

        if issave:
            for property in zpool_property:
                property['sub_id'] = pool_property_id + 1
                pool_property_sub_id = dao.backupmeta_dao.MetaPoolPropertyDAO.addpoolproperty(property,
                                                                                              database_session)

        return pool_property_sub_id, zfs_property_sub_id

    # @BaseDAO.database_operation
    def savepooldata(self, pool_data_id, poollist, database_session):
        issave = False

        if pool_data_id < 0:
            return -1
        elif poollist is None:
            return -1
        else:
            sub_id = pool_data_id + 1

        if pool_data_id > 0:
            privpooldatas = dao.backupmeta_dao.MetaPoolDAO.getprivdata(pool_data_id, database_session)
            privpooldata_size = len(privpooldatas)
        else:
            privpooldatas = None
            privpooldata_size = 0

        pooldata_size = len(poollist)
        if pooldata_size == privpooldata_size:
            equl_cnt = 0
            for pooldata in poollist:
                ashift = pooldata.get('ashift')
                pool = pooldata.get('pool')
                create_option = pooldata.get('create_option')
                for priv_pooldata in privpooldatas:
                    priv_ashift = priv_pooldata.get('ashift')
                    priv_pool = pooldata.get('pool')
                    priv_create_option = pooldata.get('create_option')
                    if priv_ashift.__eq__(ashift) and priv_pool.__eq__(pool) and priv_create_option.__eq__(create_option):
                        equl_cnt += 1
            if equl_cnt == pooldata_size:
                issave = False
            else:
                issave = True
        else:
            issave = True

        if issave:
            for pooldata in poollist:
                pooldata['sub_id'] = sub_id
                sub_id = dao.backupmeta_dao.MetaPoolDAO.addmetapooldata(pooldata, database_session)
            return sub_id
        else:
            return pool_data_id

    @BaseDAO.database_operation
    def savemetadata(self, data, database_session):
        logger.info('[setconfig] data : {}'.format(data))
        poollist = data.get('poollist')
        zpool_property = data.get('zpool_property')     # list
        zfs_property = data.get('zfs_property')         # list
        snapmeta = data.get('sanpmeta')
        nodetype = data.get('nodetype')
        usetype = data.get('usetype')
        bootdata = data.get('bootdata')
        iscsiinfo = data.get('iscsiinfo')
        name = data.get('name')

        # get priv data
        id_list = dao.backupmeta_dao.MetaDataDAO.getlastdata(data, database_session)
        if id_list is None:
            priv_id = 0
            pool_property_id = 0
            zfs_property_id = 0
            pool_data_id = 0
            snapshot_data_id = 0
            iscsiinfo_sub_id = 0
        else:
            priv_id = id_list.get('id')
            pool_property_id = id_list.get('pool_property_id')
            zfs_property_id = id_list.get('zfs_property_id')
            pool_data_id = id_list.get('pool_data_id')
            snapshot_data_id = id_list.get('snapshot_data_id')
            iscsiinfo_sub_id = id_list.get('iscsiinfo_sub_id')

        if nodetype.__eq__('MASTER'):
            pool_property_id = -1
            zfs_property_id = -1
            pool_data_id = -1
            iscsiinfo_sub_id = -1

        # logger.info('priv_id : {}'.format(priv_id))
        # logger.info('pool_property_id : {}'.format(pool_property_id))
        # logger.info('zfs_property_id : {}'.format(zfs_property_id))
        # logger.info('pool_data_id : {}'.format(pool_data_id))
        # logger.info('snapshot_data_id : {}'.format(snapshot_data_id))
        if pool_property_id > -1:
            pool_property_sub_id, zfs_property_sub_id = self.savepoolpropertydata(pool_property_id, zpool_property,
                                                                                  zfs_property_id, zfs_property, database_session)
            logging.info("poollist : {}".format(poollist))
            pool_data_sub_id = self.savepooldata(pool_data_id, poollist, database_session)
            if len(iscsiinfo) > 0:
                iscsiinfo_sub_id = dao.backupmeta_dao.IscsiInfoDAO.getsubid(data, database_session)
                if iscsiinfo_sub_id is None:
                    iscsiinfo_sub_id = 1
                else:
                    iscsiinfo_sub_id += 1
                for iscsidata in iscsiinfo:
                    iscsidata['sub_id'] = iscsiinfo_sub_id
                    dao.backupmeta_dao.IscsiInfoDAO.setdata(iscsidata, database_session)
            else:
                iscsiinfo_sub_id = -1
        else:
            pool_property_sub_id = zfs_property_sub_id = pool_data_sub_id = -1

        boot_data_id = dao.backupmeta_dao.BootDataDAO.addbootdata(bootdata, database_session)


        for snapdata in snapmeta:
            isfull = snapdata.get('isfull')
            snapname = snapdata.get('snapname')
            snapshot_data_id = dao.backupmeta_dao.SnapDataDAO.addsnapdata(snapdata, database_session)
            if 'ispolicefull' in snapdata:
                ispolicefull = snapdata.get('ispolicefull')
            else:
                ispolicefull = 0

            save_metadata = {
                'uuid': data.get('uuid'),
                'target_uuid': data.get('target_uuid'),
                'nodetype': nodetype,
                'usetype': usetype,
                'name': name,
                'snapname': snapname,
                'pool_property_id': pool_property_sub_id,
                'zfs_property_id': zfs_property_sub_id,
                'pool_data_id': pool_data_sub_id,
                'snapshot_data_id': snapshot_data_id,
                'boot_data_id': boot_data_id,
                'iscsiinfo_sub_id': iscsiinfo_sub_id,
                'islast': 1,
                'isfull': isfull,
                'ispolicefull': ispolicefull
            }


            dao.backupmeta_dao.MetaDataDAO.privlastflagchange(priv_id, database_session)
            res_data = dao.backupmeta_dao.MetaDataDAO.addmetadata(save_metadata, database_session)

        dao.backupmeta_dao.MetaDataRollbackDAO.privdatadel(data, database_session)

        res_data = {'issave': True}
        return res_data

    # {'poollist': data.get('cur_collectdata').get('cur_poollist'), 'zpool_property': zpool_propertys,
    #  'zfs_property': zfs_propertys, 'uuid': data.get('uuid'),
    #  'nodetype': data.get('nodetype'), 'usetype': data.get('usetype'),
    #  'sanpmeta': data.get('save_snap_meta')}

    def getsubdata(self, id_list, database_session):

        if id_list is None:
            return None

        pool_property_id = id_list.get('pool_property_id')
        zfs_property_id = id_list.get('zfs_property_id')
        pool_data_id = id_list.get('pool_data_id')
        snapshot_data_id = id_list.get('snapshot_data_id')
        boot_data_id = id_list.get('snapshot_data_id')
        iscsiinfo_sub_id = id_list.get('iscsiinfo_sub_id')

        poolpropertys = None
        zfspropertys = None
        pooldata = None
        snapshotdata = None
        bootdata = None
        iscsiinfo = []
        if pool_property_id > 0:
            poolpropertys = dao.backupmeta_dao.MetaPoolPropertyDAO.getprivpropertylist(pool_property_id,
                                                                                       database_session)
        if zfs_property_id > 0:
            zfspropertys = dao.backupmeta_dao.MetaTargetPropertyDAO.getprivpropertylist(zfs_property_id,
                                                                                        database_session)
        if pool_data_id > 0:
            pooldata = dao.backupmeta_dao.MetaPoolDAO.getprivdata(pool_data_id, database_session)

        if snapshot_data_id > 0:
            snapshotdata = dao.backupmeta_dao.SnapDataDAO.getprivdata(snapshot_data_id, database_session)

        if boot_data_id > 0:
            bootdata = dao.backupmeta_dao.BootDataDAO.getprivdata(boot_data_id, database_session)

        if iscsiinfo_sub_id > 0:
            iscsiinfo = dao.backupmeta_dao.IscsiInfoDAO.getlist(iscsiinfo_sub_id, database_session)

        return {'poolpropertys': poolpropertys, 'zfspropertys': zfspropertys, 'pooldata': pooldata,
                'snapdata': snapshotdata, 'bootdata': bootdata, 'iscsiinfo': iscsiinfo}

    def getsnapdatalist(self, id_list, database_session):
        if id_list is None:
            return None

        snapshot_data_id = id_list.get('snapshot_data_id')
        snapshotdata = None
        if snapshot_data_id > 0:
            snapshotdata = dao.backupmeta_dao.SnapDataDAO.getprivdata(snapshot_data_id, database_session)

        return snapshotdata

    @BaseDAO.database_operation
    def getlastsnapdata(self, data, database_session):

        id_list = dao.backupmeta_dao.MetaDataDAO.getsnapshotdata(data, True, database_session)
        subdata = self.getsubdata(id_list, database_session)

        return subdata

    @BaseDAO.database_operation
    def delincrementsnaplist(self, data, database_session):        # Compute Snap Delete list
        logger.info('DELINCREMENTSNAPLIST')
        targetsnapname = data.get('snapname')
        lastdel = dao.backupmeta_dao.MetaDataDAO.dellastsnap(data, database_session)
        dellist = []
        if lastdel is None:
            rollbacktarget = dao.backupmeta_dao.MetaDataRollbackDAO.delmanysnap(data, database_session)
            priv_file = None
            isfindsnap = False
            if rollbacktarget is not None:
                for cnt in range(0, len(rollbacktarget)):
                    for targetdata in rollbacktarget:
                        snapname = targetdata.get('snapname')
                        priv_filename = targetdata.get('priv_filename')
                        filename = targetdata.get('filename')
                        if targetsnapname.__eq__(snapname) and not isfindsnap:
                            dellist.append(targetdata)
                            priv_file = filename
                            isfindsnap = True
                        elif priv_file is not None:
                            if priv_file.__eq__(priv_filename):
                                dellist.append(targetdata)
                                priv_file = filename

        else:
            dellist.append(lastdel)
            priv_file = lastdel.get('filename')
            rollbacktarget = dao.backupmeta_dao.MetaDataRollbackDAO.delmanysnap(data, database_session)
            if rollbacktarget is not None:
                for cnt in range(0, len(rollbacktarget)):
                    for targetdata in rollbacktarget:
                        priv_filename = targetdata.get('priv_filename')
                        filename = targetdata.get('filename')

                        if priv_file.__eq__(priv_filename):
                            dellist.append(targetdata)
                            priv_file = filename
        logger.info('DELLIST [{}] : {}'.format(data.get('snapname'), dellist))
        return dellist

    @BaseDAO.database_operation
    def delonesnap(self, data, database_session):  # Compute Snap Delete list
        target = dao.backupmeta_dao.MetaDataDAO.delonesnap(data, database_session)
        if target is None:
            target = dao.backupmeta_dao.MetaDataRollbackDAO.delonesnap(data, database_session)

        return target


    @BaseDAO.database_operation
    def getrestoresnapdata(self, data, database_session):
        lastsnapname = data.get('snapname')
        snapdata = dao.backupmeta_dao.MetaDataDAO.getrestoresnapdata(data, database_session)
        if snapdata is None:
            snapdata = dao.backupmeta_dao.MetaDataRollbackDAO.getrestoresnapdata(data, database_session)
            if snapdata is None:
                return {'errorstr': 'Snapshot Data Not Found', 'errorcode':'6404'}

        snapdata_subdata = self.getsubdata(snapdata, database_session)
        data['name'] = snapdata.get('name')

        snapshotlist = dao.backupmeta_dao.MetaDataDAO.getsnapshotdata(data, False, database_session)
        snapshotlist_rollback = dao.backupmeta_dao.MetaDataRollbackDAO.getsnapshotdata(data, False, database_session)
        if snapshotlist_rollback is not None:
            for snaprollback in snapshotlist_rollback:
                snapname = snaprollback.get('snapname')
                issave = True
                if snapshotlist is not None:
                    for snapdata in snapshotlist:
                        compare_snapname = snapdata.get('snapname')
                        if compare_snapname.__eq__(snapname):
                            issave = False
                if issave:
                    snapshotlist.append(snaprollback)


        logger.info('ALL SNAPSHOTLIST [{}] : {}'.format(data.get('name'), snapshotlist))
        restore_list = None
        restore_rollback_list = None
        isrestorelast = False
        index = 0
        restorelist_reverse = []
        rollbacklist = []
        priv_snap = lastsnapname
        next_snap = lastsnapname
        logger.info("priv_snap : {} next_snap:{}".format(priv_snap, next_snap))

        for cnt in range(0, len(snapshotlist)):
            for snapdata_c in snapshotlist:
                if snapdata_c.get('priv_snapname') is not None:
                    tmp = snapdata_c.get('priv_snapname').split('@')
                    if len(tmp) > 1:
                        priv_snapname = tmp[1]
                    else:
                        priv_snapname = tmp[0]
                else:
                    priv_snapname = None
                snapname = snapdata_c.get('snapname')
                logger.info("priv_snap : {} next_snap:{}".format(priv_snapname, snapname))
                if snapname.__eq__(next_snap):
                    check_ok = True
                    logger.info("restorelist {} : priv_snapname {}".format(snapname, priv_snapname))
                    for checkdata in restorelist_reverse:
                        check_snap = checkdata.get('snapdata').get('snapname')
                        if check_snap.__eq__(snapname):
                            check_ok = False
                    if check_ok:
                        subdata = self.getsnapdatalist(snapdata_c, database_session)
                        save_data = {'snapdata': snapdata_c, 'snapinfo': subdata}
                        restorelist_reverse.append(save_data)
                        next_snap = priv_snapname
                        logger.info("save restorelist {}".format(snapname))

                if priv_snapname is not None:
                    if priv_snapname.__eq__(priv_snap):
                        check_ok = True
                        logger.info("rollbacklist {}".format(priv_snapname))
                        for checkdata in rollbacklist:
                            check_snap = checkdata.get('snapdata').get('priv_snapname')
                            if check_snap is not None:
                                check_str = check_snap.split('@')[1]
                                if check_str.__eq__(priv_snapname):
                                    check_ok = False
                        if check_ok:
                            subdata = self.getsnapdatalist(snapdata_c, database_session)
                            save_data = {'snapdata': snapdata_c, 'snapinfo': subdata}
                            rollbacklist.append(save_data)
                            priv_snap = snapname

        # restorelist_reverse.reverse()

        index = 1
        for tmp in restorelist_reverse:
            snapinfo = tmp.get('snapinfo')
            snapinfo['index'] = index
            index += 1

        index = 1
        for tmp in rollbacklist:
            snapinfo = tmp.get('snapinfo')
            snapinfo['index'] = index
            index += 1

        logger.info("RESTORE_LIST REVERSE : {}".format(restorelist_reverse))
        # logger.info("RESTORE_LIST : {}".format(restore_list))
        logger.info("ROLLBACKLIST : {}".format(rollbacklist))
        # for snapdata in snapshotlist:
        #     compare_snapname = snapdata.get('snapname')
        #     isfull = snapdata.get('isfull')
        #     ispolicebackup = snapdata.get('ispolicebackup')
        #     # subdata = self.getsubdata(snapdata, database_session)
        #     subdata = self.getsnapdatalist(snapdata, database_session)
        #     save_data = {'snapdata': snapdata, 'snapinfo': subdata}
        #     if isfull == 1 and not isrestorelast:
        #         restore_list = []
        #         subdata['index'] = 1
        #         index = 1
        #         restore_list.append(save_data)
        #     elif isfull == 0 and not isrestorelast:
        #         index += 1
        #         subdata['index'] = index
        #         restore_list.append(save_data)
        #     elif isrestorelast:
        #         index += 1
        #         subdata['index'] = index
        #         restore_rollback_list.append(save_data)
        #
        #     if compare_snapname.__eq__(lastsnapname):
        #         isrestorelast = True
        #         index = 0
        #         restore_rollback_list = []

        res_data = {
            'server_uuid': snapdata.get('server_uuid'),
            'target_uuid': snapdata.get('target_uuid'),
            'target_snapdata': snapdata_subdata,
            'restorelist': restorelist_reverse,
            'restorerollbacklist': rollbacklist
        }

        return res_data

    @BaseDAO.database_operation
    def getrestorelist(self, data, database_session):
        resstorelist = dao.backupmeta_dao.MetaDataDAO.getrestorelist(data, database_session)
        resstorelist_roll = dao.backupmeta_dao.MetaDataRollbackDAO.getrestorelist(data, database_session)
        if resstorelist_roll is not None:
            for roll in resstorelist_roll:
                resstorelist.append(roll)
        return resstorelist

    @BaseDAO.database_operation
    def restoredataupdate(self, data, database_session):
        # get all snaplist
        rollbacklist = data.get('restoredata').get('restorerollbacklist')
        logger.info("restoredataupdate rollbacklist: {}".format(rollbacklist))
        check_list = data.get('check_list')
        logger.info("restoredataupdate check_list: {}".format(check_list))
        for checkdata in check_list:
            snapdata = checkdata.get('snapdata').get('snapdata')
            issnap = dao.backupmeta_dao.MetaDataDAO.issnapname(snapdata, database_session)
            if issnap:
                isrollsnap = dao.backupmeta_dao.MetaDataRollbackDAO.issnapname(snapdata, database_session)
                if isrollsnap:
                    dao.backupmeta_dao.MetaDataRollbackDAO.privdatadel(snapdata.get('snapname'), database_session)
            else:
                dao.backupmeta_dao.MetaDataDAO.addmetadata(snapdata, database_session)
                dao.backupmeta_dao.MetaDataRollbackDAO.privdatadel(snapdata.get('snapname'), database_session)
            dao.backupmeta_dao.MetaDataDAO.setlastflagoff(snapdata.get('snapname'), database_session)

        target_snapdata = data.get('restoredata').get('target_snapdata')
        target_snapname = target_snapdata.get('snapdata').get('snapname')
        dao.backupmeta_dao.MetaDataDAO.setlastflag(target_snapname, database_session)

        if len(rollbacklist) < 1:
            return True
        for rolldata in rollbacklist:
            snapdata = rolldata.get('snapdata')
            removeid = snapdata.get('id')
            snapdata['meta_id'] = removeid
            del snapdata['id']
            rollback_id = dao.backupmeta_dao.MetaDataRollbackDAO.addmetadata(snapdata, database_session)
            dao.backupmeta_dao.MetaDataDAO.privdatadel(snapdata.get('snapname'), database_session)

        return True

    @BaseDAO.database_operation
    def restoreosupdate(self, data, database_session):
        # get all snaplist
        name = data.get('name')
        nodetype = data.get('nodetype')
        usetype = data.get('usetype')
        logger.info("name : {}, nodetype : {}, usetype : {}".format(name, nodetype, usetype))
        while True:
            lastdata = dao.backupmeta_dao.MetaDataDAO.getlastdata(data, database_session)
            logger.info("lastdata : {}".format(lastdata))
            if lastdata is None:
                break
            dao.backupmeta_dao.MetaDataDAO.setlastflagoff(lastdata.get('snapname'), database_session)

        target_snapdata = data.get('restoredata').get('target_snapdata')
        target_snapname = target_snapdata.get('snapdata').get('snapname')
        dao.backupmeta_dao.MetaDataDAO.setlastflag(target_snapname, database_session)

    @BaseDAO.database_operation
    def delsnapdata(self, data, database_session):
        dellist = data.get('dellist')
        dbdellist = []
        for delinfo in dellist:
            isdel = False
            isrollbackdel = False
            snapname = delinfo.get('snapname')
            isdel = dao.backupmeta_dao.MetaDataDAO.snapdel_setlastflag(snapname, database_session)
            if not isdel:
                isrollbackdel = dao.backupmeta_dao.MetaDataRollbackDAO.privdatadel(snapname, database_session)

            if isdel or isrollbackdel:
                dbdellist.append(delinfo)
        data['dbdellist'] = dbdellist
        return data




