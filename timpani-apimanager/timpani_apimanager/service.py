from nameko.rpc import rpc, RpcProxy
from .process.backup import ProcessBackup
from .process.restore import ProcessRestore
from .process.lock import ProcessLock
from .process.bios import BiosRunner
from .process.delete import SnapDelete

import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
stream_hander = logging.StreamHandler()
logger.addHandler(stream_hander)
#######################################################################################################################
# from .api.node import NodeAPI


class ApimanagerService(object):
    name = 'apimanager_service'

    dbmanager_rpc = RpcProxy('dbmanager_service')
    servicemanager_rpc = RpcProxy('service_manager')
    filemanager_rpc = RpcProxy('filemanager_service')
    backup_server_rpc = RpcProxy('backup_server_service')

    p_lock = ProcessLock()
    proc_backup = ProcessBackup(p_lock)
    proc_restore = ProcessRestore(p_lock)
    proc_bios = BiosRunner(p_lock)
    proc_delete = SnapDelete(p_lock)

    def db_send(self, method, msg):
        call_method = getattr(self.dbmanager_rpc, method)
        response = call_method.call_async(msg)
        return response.result()

    def service_send(self, method: object, msg: object, instance: object) -> object:
        call_method = getattr(instance, method)
        response = call_method.call_async(msg)
        return response.result()

    def ipmi_connection_check(self, data):
        is_ipmi_conn = self.service_send('ipmiConnectionCheck', data, self.servicemanager_rpc)
        if is_ipmi_conn.get('is_conn'):
            return True, is_ipmi_conn.get('node_uuid')
        else:
            return False, '-'

    @rpc
    def registerNode(self, data):
        logger.info('RegisterNode {}'.format(data))
        if 'node_uuid' in data:
            is_discover = True
            node_uuid = data.get('node_uuid')
        else:
            is_discover, node_uuid = self.ipmi_connection_check(data)

        if is_discover:
            data['node_uuid'] = node_uuid
            data['ipmi_info']['is_discovery'] = 1
        else:
            errorcode = "1001"
            errorstr = "IPMI Discovery Failed"
            responses = {'errorcode': errorcode, 'errorstr': errorstr, 'page_msg': data.get('page_msg')}
            return responses

        response = self.db_send(method='registerNode', msg=data)
        logger.info('RegisterNode Response {}'.format(response))
        return response


    # All Node List
    @rpc
    def getNodeList(self, data):
        logger.info("getNodeList {}".format(data))
        response = self.db_send(method='getNodeList', msg=data)
        return response

    # Leader Node List
    @rpc
    def getNodeLeaderList(self, data):
        logger.info("getNodeLeaderList {}".format(data))
        response = self.db_send(method='getNodeLeaderList', msg=data)
        return response


    # Compute Node List
    @rpc
    def getNodeComputeList(self, data):
        logger.info("getNodeComputeList nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='getNodeComputeList', msg=data)
        return response


    # Get Node Info
    @rpc
    def getNodeInfo(self, data):
        logger.info("getNodeInfo nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='getNodeInfo', msg=data)
        return response


    # Updete Node
    @rpc
    def updateNode(self, data):
        logger.info("updateNode: nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='updateNode', msg=data)
        return response

    # Delete Node Info
    @rpc
    def deleteNode(self, data):
        logger.info("deleteNode nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='deleteNode', msg=data)
        return response

    @rpc
    def registerIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        # IPMI COnnection Check
        is_ipmi_conn = 1
        data['is_discovery'] = is_ipmi_conn
        response = self.db_send(method='registerIPMIConn', msg=data)
        return response

    @rpc
    def updateIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        response = self.db_send(method='updateIPMIConn', msg=data)
        return response

    @rpc
    def deleteIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        response = self.db_send(method='deleteIPMIConn', msg=data)
        return response

    # Show list from Backup target source
    @rpc
    def getbackupsrclist(self, data):
        logger.info("getbackupsrclist: {}".format(data))
        response = self.db_send(method='GetBackupSrcList', msg=data)
        return response

    @rpc
    def getrecoverlist(self, data):
        logger.info("getrecoverlist: {}".format(data))
        response = self.db_send(method='GetRecoverList', msg=data)
        return response

    def rsync_full(self, node_uuid, rsync_base_data, system_info, ipmi_info):
        res_data = {
            'node_uuid' : node_uuid,
            'backup_date' : rsync_base_data.get('backup_date'),
            'home_path' : rsync_base_data.get('home_path'),
            'os' : system_info.get('os_name').lower(),
            'ipmi_info' : ipmi_info
        }
        return res_data

    def zfs_full(self, node_uuid, snap_name, home_path, system_info, ipmi_info):
        res_data = {
            'node_uuid' : node_uuid,
            'snap_name' : snap_name,
            'home_path' : home_path,
            'os' : system_info.get('os_name').lower(),
            'ipmi_info' : ipmi_info
        }
        return res_data

    def rsync_increment(self, data, rsync_base_data, system_info, ipmi_info):
        res_data = {
            'data' : data,
            'rsync_data' : rsync_base_data,
            'system_info' : system_info,
            'ipmi_info' : ipmi_info
        }
        return res_data

    @rpc
    def systemrecover(self, data):
        logger.info("systemrecover: {}".format(data))

        #Get Target Image List
        target_image_list = self.db_send(method='GetTargetImageList', msg=data)
        logger.info('target_image_list : {}'.format(target_image_list))

        #Get IPMI Information
        ipmi_info = self.db_send(method='GetIPMIInfo', msg=data)
        logger.info('ipmi_info : {}'.format(ipmi_info))

        #Get System Information
        system_info = self.db_send(method='GetSystemInfo', msg=data)

        # Get snapshot list data [DbManager]
        snapshot_list = self.db_send(method='GetSnapshotList', msg=data)
        logger.info("systemrecover response : {}".format(snapshot_list))
        data['snapshot_list'] = snapshot_list

        for target in target_image_list:
            if target.get('dataset')[0:1].__eq__('/'):
                # Linux System
                data['dataset'] = target.get('dataset')
                rsync_base_data = self.db_send(method='GetRsyncData', msg=data)
                logger.info('rsync_base_data : {}'.format(rsync_base_data))
                if data.get('recover_type').__eq__('I'):
                    send_data = self.rsync_increment(data=data,rsync_base_data=rsync_base_data,
                                                     system_info=system_info, ipmi_info=ipmi_info)
                    res_data = self.service_send(method='rsyncrecover', msg=send_data, instance=self.backup_server_rpc)
                elif data.get('recover_type').__eq__('O'):
                    send_data = self.rsync_full(node_uuid=data.get('node_uuid'), rsync_base_data=rsync_base_data,
                                                     system_info=system_info, ipmi_info=ipmi_info)
                    res_data = self.service_send(method='rsyncfullrecover', msg=send_data, instance=self.backup_server_rpc)
            else:
                # Get MetaData [DbManager]
                find_list = []
                for snap_data in snapshot_list:
                    find_list.append(snap_data.get('snapshot_name'))
                data['snapshot_find_list'] = find_list
                snap_file_data = self.db_send(method='GetSnapImageList', msg=data)
                data['snap_file_data'] = snap_file_data
                # Check snapshot image file [FileManager]
                snap_file_data = self.service_send(method='check_snapshotImage', msg=snap_file_data,
                                                   instance=self.filemanager_rpc)
                logger.info("systemrecover snap_file_data : {}".format(snap_file_data))
                home_path = ""
                for file_data in snap_file_data:
                    dir_name_split = file_data.get('image_path').split('/')
                    for dir_name in dir_name_split:
                        if dir_name.__eq__(data.get('node_uuid')):
                            break
                        if len(dir_name) > 0:
                            home_path = "{}/{}".format(home_path, dir_name)
                    break

                logger.info("home_path : {}".format(home_path))

                if data.get('recover_type').__eq__('I'):
                    # Recover [Recover]
                    res_data = self.service_send(method='systemrecover', msg=data, instance=self.servicemanager_rpc)
                elif data.get('recover_type').__eq__('O'):
                    send_data = self.zfs_full(node_uuid=data.get('node_uuid'), snap_name=data.get('snapname'), home_path=home_path,
                             system_info=system_info, ipmi_info=ipmi_info)
                    logger.info("send_data {}".format(send_data))
                    res_data = self.service_send(method='zfsfullrecover', msg=send_data,
                                                 instance=self.backup_server_rpc)


        return res_data

    @rpc
    def setsystemhistory(self, data):
        logger.info("setsystemhistory: {}".format(data))
        if 'action_msg' in data:
            data['action_message'] = data['action_msg']
        if 'action_err_code' in data:
            data['err_code'] = data['action_err_code']
        if 'action_err_msg' in data:
            data['err_message'] = data['action_err_msg']
        response = self.db_send(method='processhistory', msg=data)
        return response

    # Get Backup & Recover & Error history
    @rpc
    def getsystemhistory(self, data):
        logger.info("getsystemhistory: {}".format(data))
        response = self.db_send(method='GetSystemHistory', msg=data)
        return response

    @rpc
    def getsystemprocesshistory(self, data):
        logger.info("getsystemhistory: {}".format(data))
        response = self.db_send(method='GetSystemProcessHistory', msg=data)
        return response

    @rpc
    def systembackup(self, data):
        logger.info("systembackup: {}".format(data))
        target_list = data['backup_target']
        rsync_backup = False
        zfs_backup = False
        for target_kind in target_list:
            if target_kind[0:1].__eq__('/'):
                rsync_backup = True
            else:
                zfs_backup = True

        response = self.db_send(method='GetSystemInfo', msg=data)

        if rsync_backup:
            data['os_type'] = response.get('os_type')
            data['os_name'] = response.get('os_name')
            data['ipaddress'] = response.get('ipaddress')
            logger.info("data : {}".format(data))
            if data.get('backup_type').__eq__('I'):
                res_data = self.service_send(method='rsyncbackup', msg=data, instance=self.backup_server_rpc)
            elif data.get('backup_type').__eq__('F'):
                res_data = self.service_send(method='rsyncfullbackup', msg=data, instance=self.backup_server_rpc)
            
        if zfs_backup:
            res_data = self.service_send(method='systembackup', msg=data, instance=self.servicemanager_rpc)

        return res_data

############################################ DATA SYNC #################################################

    @rpc
    def synccheck(self, data):
        # data : {'sync_proc': '', sync_name': timapni_base.constants.SYNC_NAME_NODE}
        logger.info("[SYNCCHECK] data : {}".format(data))
        # Check Sync Data (DB)
        response = self.db_send(method='synccheck', msg=data)
        # response : {'result':'true' or 'false'}
        return response

    @rpc
    def mastersync(self, data):
        logger.info("[MASTER ACCOUNT SYNC] data : {}".format(data))
        response = self.db_send(method='mastersync', msg=data)
        return response

    @rpc
    def masterinfo(self, data):
        logger.info("[MASTER INFORMATION] data : {}".format(data))
        response = self.db_send(method='masterinfo', msg=data)
        return response

############################################# Backup #####################################################
    # Get Target List


    def findmodulename(self, nodetype, data, moduletype):
        if nodetype.upper().__eq__('COMPUTE'):
            find_data = {'nodetype': 'STORAGE', 'moduletype': moduletype}
        elif nodetype.upper().__eq__('MASTER'):
            find_data = {'nodetype':'MASTER', 'moduletype': moduletype}
        elif nodetype.upper().__eq__('STORAGE'):
            find_data = {'nodetype': 'STORAGE', 'moduletype': moduletype}
        elif nodetype.upper().__eq__('BIOS'):
            find_data = {'moduletype': moduletype}
        elif nodetype.upper().__eq__('FILEMANAGER'):
            find_data = {'moduletype': moduletype}

        getmodulename = self.db_send('appgetmodulename', find_data)
        target_uuid = None
        res_modulename = None
        server_uuid = None
        if 'uuid' in data:
            if data.get('uuid') is None:
                target_uuid = None
            else:
                target_uuid = data.get('uuid').replace('-', '').upper()
        else:
            target_uuid = None

        logger.info("[Get Node Type] getnodetype_dic : {}".format(getmodulename))
        if isinstance(getmodulename, list):
            list_size = len(getmodulename)
            for modulename in getmodulename:
                if list_size == 1:
                    res_modulename = modulename.get('modulename')
                    server_uuid = modulename.get('uuid')
                    if target_uuid is None:
                        target_uuid = server_uuid
                else:
                    tmp_uuid = modulename.get('uuid')
                    if target_uuid is not None:
                        if tmp_uuid.__eq__(target_uuid):
                            server_uuid = modulename.get('uuid')
                            res_modulename = modulename.get('modulename')
                    else:
                        errorcode = "1021"
                        errorstr = "Failed Backup"
                        response = {'errorcode': errorcode, 'errorstr': errorstr}
                        return response
        else:
            if getmodulename is not None:
                res_modulename = getmodulename.get('modulename')
                server_uuid = getmodulename.get('uuid')
            else:
                errorcode = "1021"
                errorstr = "Failed Backup"
                response = {'errorcode': errorcode, 'errorstr': errorstr}
                return response

        return res_modulename, server_uuid, target_uuid


    # Backup Command
    @rpc
    def backupcmd(self, data):
        # {"uuid":"PHY NODE UUID", "usetype" : "ORIGIN, OS, DATA", "nodetype" : "MASTER, STORAGE, COMPUTE"
        # , "name" : "volume name"}
        nodetype = data.get('nodetype')
        usetype = data.get('usetype')

        if nodetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif nodetype.upper().__eq__('MASTER') or usetype.upper().__eq__('STORAGE') or usetype.upper().__eq__(
                'COMPUTE'):
            iscontinue = True
        else:
            iscontinue = False

        if usetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif usetype.upper().__eq__('OS') or usetype.upper().__eq__('ORIGIN') or usetype.upper().__eq__('DATA'):
            iscontinue = True
        else:
            iscontinue = False

        if not iscontinue:
            err_code = "1004"
            err_message = "Parameter Data miss matching"
            return {'err_code': err_code, 'err_message': err_message}

        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'backup')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))

        if modulename is None:
            err_code = "4001"
            err_message = "Node Connection Failed"
            return {'err_code': err_code, 'err_message': err_message}

        data['target_uuid'] = target_uuid
        data['server_uuid'] = server_uuid
        data['modulename'] = modulename

        ischeckconfigdata = False
        if nodetype.__eq__('MASTER'):
            config_data = {'get_kind': nodetype}
            getconfigdata = self.db_send('getappconfig', config_data)
            data['configdata'] = getconfigdata
            ischeckconfigdata = True
        elif nodetype.__eq__('STORAGE'):
            config_data = {'get_kind': nodetype}
            getconfigdata = self.db_send('getappconfig', config_data)
            data['configdata'] = getconfigdata
            ischeckconfigdata = True

        if ischeckconfigdata:
            if getconfigdata is None:
                errcode = '4000'
                errmsg = 'DB Not Found Data'
                return {'err_code': errcode, 'err_message': errmsg}

            if 'errorcode' in getconfigdata:
                errcode = getconfigdata.get('errorcode')
                errmsg = getconfigdata.get('errorstr')
                return {'err_code': errcode, 'err_message': errmsg}

        # GET NFS INFO
        nfs_data = {'get_kind': 'NFS'}
        getconfigdata = self.db_send('getappconfig', nfs_data)
        if getconfigdata is None:
            errcode = '4000'
            errmsg = 'DB Not Found Data'
            return {'err_code': errcode, 'err_message': errmsg}

        if 'errorcode' in getconfigdata:
            errcode = getconfigdata.get('errorcode')
            errmsg = getconfigdata.get('errorstr')
            return {'err_code': errcode, 'err_message': errmsg}

        data['nfs_server'] = getconfigdata.get('backup_ip')
        data['export_path'] = getconfigdata.get('nfs_export_path')
        data['mount_path'] = getconfigdata.get('nfs_mount_path')
        logger.info("NFS CONFIG DATA : {}".format(getconfigdata))
        res = self.proc_backup.run(data)
        return res


    @rpc
    def restorecmd(self, data):
        # { "usetype" : "ORIGIN, OS, DATA", "nodetype" : "MASTER, STORAGE, COMPUTE"
        # , "name" : "volume name", "isboot": true or false, "snapname": "snapname}

        nodetype = data.get('nodetype')
        usetype = data.get('usetype')

        iscontinue = False

        if nodetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif nodetype.upper().__eq__('MASTER') or usetype.upper().__eq__('STORAGE') or usetype.upper().__eq__('COMPUTE'):
            iscontinue = True
        else:
            iscontinue = False

        if usetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif usetype.upper().__eq__('OS') or usetype.upper().__eq__('ORIGIN') or usetype.upper().__eq__('DATA'):
            iscontinue = True
        else:
            iscontinue = False

        if not iscontinue:
            err_code = "1004"
            err_message = "Parameter Data miss matching"
            return {'err_code': err_code, 'err_message': err_message}

        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'restore')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))
        isfailed =False

        if modulename is None or modulename.__eq__(''):
            err_code = "4001"
            err_message = "Node Connection Failed"
            return {'err_code': err_code, 'err_message': err_message}
        data['modulename'] = modulename

        if nodetype.__eq__('COMPUTE'):
            restoredata = self.db_send('getrestoresnapdata', data)

            if 'errorcode' in restoredata:
                errcode = restoredata.get('errorcode')
                errmsg = restoredata.get('errorstr')
                return {'err_code': errcode, 'err_message': errmsg}
            data['restoredata'] = restoredata
            data['name'] = restoredata.get('target_snapdata').get('snapdata').get('dataset')
            logger.info("target restoredata : {}".format(restoredata.get('target_snapdata')))
            logger.info("restoredata : {}".format(restoredata))
            if 'server_uuid' in restoredata:
                if restoredata.get('server_uuid') is None:
                    data['server_uuid'] = server_uuid
                else:
                    data['server_uuid'] = restoredata.get('server_uuid')
            else:
                data['server_uuid'] = server_uuid

            if 'target_uuid' in restoredata:
                if restoredata.get('target_uuid') is None:
                    data['target_uuid'] = target_uuid
                else:
                    data['target_uuid'] = restoredata.get('target_uuid')
            else:
                data['target_uuid'] = server_uuid
        else:
            restoredata = self.db_send('getrestoresnapdata', data)
            data['name'] = restoredata.get('target_snapdata').get('snapdata').get('dataset')
            if 'errorcode' in restoredata:
                errcode = restoredata.get('errorcode')
                errmsg = restoredata.get('errorstr')
                return {'err_code': errcode, 'err_message': errmsg}
            data['restoredata'] = restoredata
            data['server_uuid'] = server_uuid
            data['target_uuid'] = target_uuid

        # GET NFS INFO
        nfs_data = {'get_kind': 'NFS'}
        getconfigdata = self.db_send('getappconfig', nfs_data)
        logger.info("NFS GETCONFIGDATA : {}".format(getconfigdata))
        if getconfigdata is None:
            logger.info("NFS GETCONFIGDATA aaa : {}".format(getconfigdata))
            errcode = '4000'
            errmsg = 'DB Not Found Data'
            return {'err_code': errcode, 'err_message': errmsg}

        if 'errorcode' in getconfigdata:
            errcode = getconfigdata.get('errorcode')
            errmsg = getconfigdata.get('errorstr')
            return {'err_code': errcode, 'err_message': errmsg}

        data['nfs_server'] = getconfigdata.get('backup_ip')
        data['export_path'] = getconfigdata.get('nfs_export_path')
        data['mount_path'] = getconfigdata.get('nfs_mount_path')
        logger.info("NFS CONFIG DATA : {}".format(getconfigdata))
        logger.info("DATA : {}".format(data))
        res = self.proc_restore.run(data)

        return res

    @rpc
    def deletecmd(self, data):
        # { "usetype" : "ORIGIN, OS, DATA", "nodetype" : "MASTER, STORAGE, COMPUTE"
        # , "name" : "volume name", "isboot": true or false, "snapname": "snapname}

        nodetype = data.get('nodetype')
        usetype = data.get('usetype')

        iscontinue = False

        if nodetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif nodetype.upper().__eq__('MASTER') or usetype.upper().__eq__('STORAGE') or usetype.upper().__eq__(
                'COMPUTE'):
            iscontinue = True
        else:
            iscontinue = False

        if usetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif usetype.upper().__eq__('OS') or usetype.upper().__eq__('ORIGIN') or usetype.upper().__eq__('DATA'):
            iscontinue = True
        else:
            iscontinue = False

        if not iscontinue:
            err_code = "1004"
            err_message = "Parameter Data miss matching"
            return {'err_code': err_code, 'err_message': err_message}

        modulename, server_uuid, target_uuid = self.findmodulename('FILEMANAGER', data, 'filemanager')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))
        isfailed = False

        if modulename is None or modulename.__eq__(''):
            err_code = "4001"
            err_message = "Node Connection Failed"
            return {'err_code': err_code, 'err_message': err_message}
        data['modulename'] = modulename

        if nodetype.__eq__('COMPUTE'):
            dellist = self.db_send('delincrementsnaplist', data)

            if 'errorcode' in dellist:
                errcode = dellist.get('errorcode')
                errmsg = dellist.get('errorstr')
                return {'err_code': errcode, 'err_message': errmsg}

            if len(dellist) == 0:
                errcode = "8404"
                errmsg = "Target snap file delete not possible"
                return {'err_code': errcode, 'err_message': errmsg}

            data['dellist'] = dellist
            # deldatalist = dellist.get('dellist')
            for datainfo in dellist:
                if datainfo.get('server_uuid') is None:
                    data['server_uuid'] = server_uuid
                else:
                    data['server_uuid'] = datainfo.get('server_uuid')

                if datainfo.get('target_uuid') is None:
                    data['target_uuid'] = target_uuid
                else:
                    data['target_uuid'] = datainfo.get('target_uuid')

        else:
            if usetype.__eq__('DATA') and nodetype.__eq__('MASTER'):
                dellist = self.db_send('delincrementsnaplist', data)
                # deldatalist = dellist.get('dellist')
                for datainfo in dellist:
                    if datainfo.get('server_uuid') is None:
                        data['server_uuid'] = server_uuid
                    else:
                        server_uuid = datainfo.get('server_uuid')

                    if datainfo.get('target_uuid') is None:
                        data['target_uuid'] = target_uuid
                    else:
                        target_uuid = datainfo.get('target_uuid')

            else:
                dellist = []
                target = self.db_send('delonesnap', data)
                if target is None:
                    errcode = "8405"
                    errmsg = "Target snap file not found"
                    return {'err_code': errcode, 'err_message': errmsg}
                dellist.append(target)
                server_uuid = target.get('server_uuid')
                target_uuid = target.get('target_uuid')

            if 'errorcode' in dellist:
                errcode = dellist.get('errorcode')
                errmsg = dellist.get('errorstr')
                return {'err_code': errcode, 'err_message': errmsg}

            data['dellist'] = dellist
            data['server_uuid'] = server_uuid
            data['target_uuid'] = target_uuid

        # GET NFS INFO
        nfs_data = {'get_kind': 'NFS'}
        getconfigdata = self.db_send('getappconfig', nfs_data)
        logger.info("NFS GETCONFIGDATA : {}".format(getconfigdata))
        if getconfigdata is None:
            logger.info("NFS GETCONFIGDATA aaa : {}".format(getconfigdata))
            errcode = '4000'
            errmsg = 'DB Not Found Data'
            return {'err_code': errcode, 'err_message': errmsg}

        if 'errorcode' in getconfigdata:
            errcode = getconfigdata.get('errorcode')
            errmsg = getconfigdata.get('errorstr')
            return {'err_code': errcode, 'err_message': errmsg}

        data['nfs_server'] = getconfigdata.get('backup_ip')
        data['export_path'] = getconfigdata.get('nfs_export_path')
        data['mount_path'] = getconfigdata.get('nfs_mount_path')
        logger.info("NFS CONFIG DATA : {}".format(getconfigdata))
        logger.info("DATA : {}".format(data))
        res = self.proc_delete.run(data)

        return res

    @rpc
    def getdatadir(self, data):
        res = self.db_send('getdatadir', data)
        return res

    @rpc
    def getnodetype(self, data):
        logger.info("[Get Node Type] data : {}".format(data))
        getnodetype_dic = self.db_send('getnodetype', data)
        logger.info("[Get Node Type] getnodetype_dic : {}".format(getnodetype_dic))

        if 'nodetype' in getnodetype_dic:
            if getnodetype_dic.get('nodetype') is not None:
                nodetype = getnodetype_dic.get('nodetype').upper()
            else:
                errorcode = "1011"
                errorstr = "Failed Get NodeType"
                response = {'errorcode': errorcode, 'errorstr': errorstr}
                return response
        else:
            errorcode = "1011"
            errorstr = "Failed Get NodeType"
            response = {'errorcode': errorcode, 'errorstr': errorstr}
            return response

        data['get_kind'] = nodetype
        getconfigdata = self.db_send('getappconfig', data)
        resdata = {'nodetype':nodetype, 'configdata':getconfigdata}
        return resdata

    @rpc
    def getbiosconfig(self, data):
        data['get_kind'] = 'IPMI'
        getconfigdata = self.db_send('getappconfig', data)
        resdata = {'nodetype': 'BIOS', 'configdata': getconfigdata}
        return resdata

    @rpc
    def addservice(self, data):
        logger.info("[AddService] data : {}".format(data))
        res = self.db_send('addservice', data)
        return res

    @rpc
    def keepalive(self, data):
        logger.info("[keepalive] data : {}".format(data))
        res = self.db_send('keepalive', data)
        return res

    @rpc
    def getrealhist(self, data):
        res = self.db_send('getrealhist', data)
        return res

    @rpc
    def getprocesshist(self, data):
        res = self.db_send('getprocesshist', data)
        return res

    @rpc
    def getrestorelist(self, data):
        res = self.db_send('getrestorelist', data)
        return res

    @rpc
    def setbiostemplatedata(self, data):
        nodetype = 'BIOS'
        if data is None:
            data = {}
        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'bios')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))

        if modulename is None:
            errorcode = "1022"
            errorstr = "Not Found ModuleName"
            response = {'errorcode': errorcode, 'errorstr': errorstr}
            return response

        res_data = self.proc_bios.template_init(modulename)
        res = self.db_send('setbiostemplatedata', res_data)
        return res

    @rpc
    def biosconfig(self, data):
        nodetype = 'BIOS'
        if data is None:
            data = {}
        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'bios')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))

        if modulename is None:
            errorcode = "1022"
            errorstr = "Not Found ModuleName"
            response = {'errorcode': errorcode, 'errorstr': errorstr}
            return response

        data['server_uuid'] = server_uuid
        data['target_uuid'] = target_uuid
        data['modulename'] = modulename

        # GET NFS INFO
        nfs_data = {'get_kind': 'NFS'}
        getconfigdata = self.db_send('getappconfig', nfs_data)

        if getconfigdata is None:
            logger.info("NFS GETCONFIGDATA aaa : {}".format(getconfigdata))
            errcode = '4000'
            errmsg = 'DB Not Found Data'
            return {'err_code': errcode, 'err_message': errmsg}

        if 'errorcode' in getconfigdata:
            errcode = getconfigdata.get('errorcode')
            errmsg = getconfigdata.get('errorstr')
            return {'err_code': errcode, 'err_message': errmsg}

        data['nfs_server'] = getconfigdata.get('backup_ip')
        data['export_path'] = getconfigdata.get('nfs_export_path')
        data['mount_path'] = getconfigdata.get('nfs_mount_path')

        res = self.proc_bios.run(data)
        return res

    @rpc
    def gettemplatelist(self, data):
        res = self.db_send('gettemplatelist', data)
        return res

    @rpc
    def settemplate(self, data):
        nodetype = 'BIOS'
        if data is None:
            data = {}
        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'bios')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))

        if modulename is None:
            errorcode = "1022"
            errorstr = "Not Found ModuleName"
            response = {'errorcode': errorcode, 'errorstr': errorstr}
            return response

        data['server_uuid'] = server_uuid
        data['target_uuid'] = target_uuid
        getdata = self.db_send('getbiostemplatedata', data)
        logger.info("get template data: {}".format(getdata))

        return getdata

    @rpc
    def getnodelist(self, data):
        return self.db_send('getnodelist', data)

    @rpc
    def getvolumelist(self, data):
        return self.db_send('getvolumelist', data)

    @rpc
    def sensorcollect(self, data):
        logger.info("==================== SENSOR COLLECT =============================")
        nodetype = 'BIOS'
        if data is None:
            data = {}
        modulename, server_uuid, target_uuid = self.findmodulename(nodetype, data, 'bios')
        logger.info("modulename: {}\nserver_uuid: {}\ntarget_uuid: {}".format(modulename, server_uuid, target_uuid))

        if modulename is None:
            errorcode = "1022"
            errorstr = "Not Found ModuleName"
            response = {'errorcode': errorcode, 'errorstr': errorstr}
            return response

        nodelist = self.db_send('getnodelist', None)
        ipmilist = []
        for nodedata in nodelist:
            user = nodedata.get('ipmi_user_id')
            passwd = nodedata.get('ipmi_user_password')
            ip = nodedata.get('bmc_ip')
            macaddr = nodedata.get('bmc_mac_addr')
            nodetype = nodedata.get('node_name')
            if nodetype.upper().__eq__('COMPUTE'):
                target_uuid = nodedata.get('server_uuid')
            else:
                target_uuid = nodedata.get('uuid')
            ipmilist.append({'user':user, 'passwd':passwd, 'ip':ip, 'macaddr':macaddr,
                             'nodetype': nodetype.upper(), 'target_uuid':target_uuid})
        data['ipmilist'] = ipmilist
        res_data = self.proc_bios.getsensor(modulename, data)
        res_data = self.db_send('setipmisensor', res_data)
        # res = self.db_send('setbiostemplatedata', res_data)
        return res_data

    @rpc
    def setdatadir(self, data):
        res = self.db_send('setdatadir', data)
        return res

    @rpc
    def getdatadir(self, data):
        res = self.db_send('getdatadir', data)
        return res

    @rpc
    def getcurtemplate(self, data):
        res = self.db_send('getcurtemplate', data)
        return res

    @rpc
    def getsyscfgdumplist_api(self, data):
        res = self.db_send('getsyscfgdumplist', data)
        return res

    @rpc
    def getsyscfgdumpdata_api(self, data):
        res = self.db_send('getsyscfgdumpdata', data)
        return res


