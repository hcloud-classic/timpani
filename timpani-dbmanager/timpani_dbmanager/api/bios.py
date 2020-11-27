import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class BiosAPI(object):
    base = Base()

    @BaseDAO.database_operation
    def registerBiosInfo(self, data, database_session):
        # logger.info('registerBiosInfo {}'.format(data))

        def Check_Avail(avail_data):
            logger.info("[Check_Avail : {}".format(avail_data))
            avail_key = []
            for avail_obj in avail_data:
                key = avail_obj.get('avail_key')
                avail_key.append(key)
            logger.info("==================")
            avail_check_data = {'in_data': avail_key}
            logger.info("==================")
            result, avail_id = dao.bios_dao.BiosOptionsAvailDAO.check_avail_data(avail_check_data, database_session)
            logger.info("[check_avail] result : {}, avail_id : {}".format(result, avail_id))
            if result:
                return avail_id
            else:
                # avail list table insert
                avail_list_data = {'list_cnt': len(avail_key)}
                avail_id = dao.bios_dao.BiosOptionsAvailListDAO.register_biosoptionsavaillist(avail_list_data, database_session)
                for avail_value in avail_key:
                    temp_data = {'key': avail_value, 'key_id' : '', 'avail_list_id' : avail_id}
                    avail_save_id = dao.bios_dao.BiosOptionsAvailDAO.register_biosoptionsavail(temp_data, database_session)

            return avail_id
            # if isinstance(check_avail,list):
            #     for avail_val in avail_data:


        res_data = {}
        # 'tb_bios' table check
        # if not dao.bios_dao.BaseDAO.check_bios_table(data, database_session):
        #     # 'tb_bios' table not exist
        #     # Create Bios Table
        #     new_bios_data = {"node_uuid": data.get('node_uuid'), "bios_version": '', "firmware_version" : ''}
        #     bios_id, _ = dao.bios_dao.BaseDAO.register_bios(new_bios_data, database_session)

        config_data = data.get('bios_config')
        #Create Config Table
        # default_config_table_templte = {'node_uuid': data.get('node_uuid'), 'bios_id': bios_id, 'isdefault': 0, 'iscurrent': 1, 'config_list_id': 0}
        config_id = 0
        #Save Config Data
        for section_data in config_data:
            logger.info("section_data : {}".format(section_data))
            section_key = section_data.get('section_key')
            logger.info("section_key : {}".format(section_key))
            options = section_data.get('options')
            logger.info("options : {}".format(options))
            for option_data in options:
                availe = option_data.get('available')
                logger.info("availe : {}".format(availe))
                #available save
                if len(availe) > 0:
                    logger.info("===========")
                    avail_id = Check_Avail(availe)
                else:
                    avail_id = 0

                option_data = {
                    'config_list_id' : 1,
                    'section_key' : section_key,
                    'key': option_data.get('key'),
                    'value': option_data.get('value'),
                    'avail_list_id': avail_id,
                    'viewtype':''
                }
                option_id = dao.bios_dao.BiosOptionsDAO.register_biosoptions(option_data, database_session)



        # default_option_table_templte = {'config_list_id' : config_id, 'section_key' : config_data.get('section_key'), 'key': config_data.get('options').get('key')}


        # data['node_uuid'] = str(uuid.uuid4())
        # _, node_uuid = dao.ipmi_dao.IpmiDAO.register_ipmi_connection_info(data, database_session=database_session)
        # res_data['nodeuuid'] = str(node_uuid)
        return res_data

    @BaseDAO.database_operation
    def updateBios(self, data, database_session):
        logger.info('updateIPMIConn {}'.format(data))
        ## conn_id ==> node_uuid
        res_data = {}
        data['node_uuid'] = data.get('conn_id')
        node_uuid = dao.ipmi_dao.IpmiDAO.update_ipmi_connection_info(data, database_session=database_session)
        res_data['nodeuuid'] = str(node_uuid)
        return res_data

    @BaseDAO.database_operation
    def deleteBios(self, data, database_session):
        logger.info('deleteIPMIConn {}'.format(data))
        res = dao.ipmi_dao.IpmiDAO.del_ipmi_connection_info(node_uuid=data.get('conn_id'), database_session=database_session)
        if res.__eq__('0'):
            return {'result': '0', 'resultmsg': 'Data deletion failure'}
        else:
            return {'result':'1', 'resultmsg':'Data deletion complete'}

