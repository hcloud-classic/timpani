import logging
import re
import copy
import platform
from ..zfs import ZFS
from .iscsi import IscsiProc

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class zvolMetaData(object):

    def __init__(self, name, isIncrement):
        self.volume_name = name
        self.isIncrement = isIncrement

    def zfslist_parser(self, sp_output, issnap, vol_name, isall=False):
        # logger.info(sp_output)
        ZFSLIST_HEADER_LIST = ["zfs_name", "zfs_used_size", "zfs_avail_size", "zfs_ref_size", "zfs_mount_point"]

        i = 0
        linecount = 0
        res = []
        issave = False
        for raw in sp_output:
            if i == 0:
                line = {}
            if not isall:
                if ZFSLIST_HEADER_LIST[i].__eq__('zfs_name'):
                    if issnap:
                        compare_str = vol_name+'@'
                        pattern = re.compile(compare_str)
                        if pattern.search(raw):
                            logger.info("MATCH SNAPSHOT : {}".format(raw))
                            issave = True
                    else:
                        issave = True

            line[ZFSLIST_HEADER_LIST[i]] = raw

            i += 1
            i %= 5

            if i == 0:
                if issave or isall:
                    linecount += 1
                    line['index'] = linecount
                    res.append(line)

                issave = False

        return res, linecount

    def searchdataset_parser(self, sp_output, vol_name):
        logger.info(sp_output)
        ZFSLIST_HEADER_LIST = ["zfs_name", "zfs_used_size", "zfs_avail_size", "zfs_ref_size", "zfs_mount_point"]
        logger.info("[searchdataset_parser] vol_name : {}".format(vol_name))
        i = 0
        linecount = 0
        res = []
        issave = False
        for raw in sp_output:
            if i == 0:
                line = {}
            if ZFSLIST_HEADER_LIST[i].__eq__('zfs_name'):
                if vol_name.__eq__(raw):
                    issave=True

                compare_str = vol_name
                orig_raw = copy.deepcopy(raw)
                sp_data = raw.split('/')
                sp_length = 0
                if sp_data is not None:
                    sp_length = len(sp_data)
                    data_offset = 0
                    for sp_val in sp_data:
                        pattern = re.compile(compare_str)
                        data_offset += 1
                        if pattern.search(sp_val):
                            if data_offset == sp_length:
                                logger.info("MATCH SNAPSHOT : {}".format(orig_raw))
                                issave = True
            line[ZFSLIST_HEADER_LIST[i]] = raw

            i += 1
            i %= 5

            if i == 0:
                if issave:
                    linecount += 1
                    line['index'] = linecount
                    res.append(line)
                issave = False

        return res, linecount

    def property_parser(self, sp_output):

        ZPOOL_RESULT_TEMPLETE = {'dataset': None, 'property': None, 'value': None, 'source': None}
        logger.info("sp_output : {}".format(sp_output))
        result_data = []
        bootpool = None
        bootpath = None
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) == 4:
                dataset = values[0]
                property = values[1] if not values[1].__eq__('-') else None
                property_value = values[2] if not values[2].__eq__('-') else None
                property_source = values[3] if not values[3].__eq__('-') else None
                if property.__eq__('bootfs'):
                    bootpool = dataset
                    bootpath = property_value
                result_data.append({'dataset': dataset,
                                    'property': property,
                                    'value': property_value,
                                    'source': property_source})
        return result_data, bootpool, bootpath

    def zdb_parser(self, sp_output):
        logger.info("sp_output : {}".format(sp_output))
        line_cnt = 0
        cur_findtype = 0
        zpool_device_struct = []
        istree = False
        disk_list = None
        priv_parsingdata = None
        poollist = []
        pooldata = None
        for raw in sp_output:
            logger.info("line [{}] : {}".format(line_cnt, raw.strip()))
            sp_data = raw.strip().split(':')
            if sp_data[0].__eq__('name'):
                value = sp_data[1].replace('\'',' ').strip()
                logger.info("[name] : {}".format(value))
                if pooldata is not None:
                    if treedata is not None:
                        pooldata['treedata'].append(treedata)
                        pooldata['disk_total_cnt'] += len(treedata['disklist'])
                        if treedata['treetype'].__eq__('stripe'):
                            add_print_cnt = 0
                        else:
                            add_print_cnt = 1
                        pooldata['print_cnt'] += add_print_cnt
                    poollist.append(pooldata)
                treetype = None
                isdiskstart = False
                istree =False
                ischange = True
                treedata = None
                pooldata = {'pool': value, 'ashift' : -1, 'disk_total_cnt': 0, 'print_cnt': 0, 'treedata': []}
                priv_disk_id = 0
            elif sp_data[0].__eq__('type'):
                value = sp_data[1].replace('\'',' ').strip()
                logger.info("[type] : {}".format(value))
                if value.__eq__('raidz') or value.__eq__('mirror'):
                    treetype = value
                    if treedata is not None:
                        pooldata['treedata'].append(treedata)
                        treedata = None
                    istree = True
                    isdiskstart = False
                elif value.__eq__('disk'):
                    if not isdiskstart:
                        isdiskstart = True
            elif sp_data[0].__eq__('id'):
                value = sp_data[1].replace('\'', ' ').strip()
                logger.info("[id] : {}".format(value))
                if isinstance(value,str):
                    int_value = int(value)
                elif isinstance(value, int):
                    int_value = value
                disk_id = int_value
                if istree and not isdiskstart:
                    tree_id = int_value
                    if treedata is None:
                        treedata = {'id': tree_id, 'treetype': treetype, 'disklist':[]}
                elif not istree and isdiskstart:
                    if treedata is None:
                        treedata = {'id': -1, 'treetype': 'stripe', 'disklist': []}
                priv_disk_id = disk_id
            elif sp_data[0].__eq__('path'):
                value = sp_data[1].replace('\'', ' ').strip()
                logger.info("[path] : {}".format(value))
                treedata['disklist'].append({'id': disk_id, 'path': value})
            elif sp_data[0].__eq__('ashift'):
                value = sp_data[1].replace('\'', ' ').strip()
                logger.info("[ashift] : {}".format(value))
                if isinstance(value,str):
                    int_value = int(value)
                elif isinstance(value, int):
                    int_value = value
                ashift = int_value
                pooldata['ashift'] = ashift
            line_cnt += 1

        if pooldata is not None:
            if treedata is not None:
                pooldata['treedata'].append(treedata)
                pooldata['disk_total_cnt'] += len(treedata['disklist'])
                if treedata['treetype'].__eq__('stripe'):
                    add_print_cnt = 0
                else:
                    add_print_cnt = 1
                pooldata['print_cnt'] += add_print_cnt
            poollist.append(pooldata)


        logger.info("zdb data : {}".format(poollist))

        return poollist

    def status_parser(self, sp_output):
        logger.info("sp_output : {}".format(sp_output))
        create_option = None
        find_str = ['raidz','mirror']
        for raw in sp_output:
            if not raw.strip().__eq__('NAME'):
                save_word = None
                for str_word in find_str:
                    pattern = re.compile(str_word)
                    if pattern.search(raw.strip()):
                        save_word = raw.split('-')[0]
                if save_word is None:
                    save_word = raw.strip()
                if create_option is None:
                    create_option = save_word
                else:
                    create_option += " " + save_word
        return create_option

    def collect_zfssnapshotlist(self, isall=False):
        result = None
        line_cnt = -1
        try:
            stdout = ZFS.zfs_list(target=None, zfs_types=["snapshot"])
            line = stdout.split()
            logger.info("LINE : {}".format(line))
            result, line_cnt = self.zfslist_parser(line, True, self.volume_name, isall)
            logger.info("zfs snapshot list count : {}".format(line_cnt))
            logger.info("zfs snapshot list data : {}".format(result))
        except Exception as e:
            logger.info("[collect_zfslist] EXCEPT : {}".format(e))

        return result, line_cnt

    def searchdataset(self, zfstype):
        datasets = []
        line_cnt = -1
        try:
            stdout = ZFS.zfs_list(target=None, zfs_types=[zfstype])
            line = stdout.split()
            result, line_cnt = self.searchdataset_parser(line, self.volume_name)
            logger.info("zfs list count : {}".format(line_cnt))
            logger.info("zfs list data : {}".format(result))
            if line_cnt > 0:
                for dataset in result:
                    sp_data = dataset.get('zfs_name').split('/')
                    zpool_name = sp_data[0]
                    datasets.append((zpool_name, dataset.get('zfs_name')))

        except Exception as e:
            logger.info("[searchvolumedataset] EXCEPT : {}".format(e))

        return datasets, line_cnt

    def collect_zfsproperty(self, datasets, zfstype):
        propertys = []
        zpool_propertys = []
        bootpool = None
        bootpath = None
        try:
            for zpool_name, dataset in datasets:
                # ZFS PROPERTY
                output = ZFS.zfs_get(target=dataset)
                sp_output = output.split('\n')
                property, bootpool, bootpath = self.property_parser(sp_output)
                propertys.append({'propertykind': 'zfs','dataset':dataset, 'zpool': zpool_name, 'zfstype': zfstype, 'propertys': property})

                # ZPOOL PROPERTY
                zpool_property_save = True
                for pool_property in zpool_propertys:
                    if pool_property.get('zpool').__eq__(zpool_name):
                        zpool_property_save = False

                if zpool_property_save:
                    logger.info("zpool get pool name : {}".format(zpool_name))
                    output = ZFS.zpool_get(pool=zpool_name)
                    sp_output = output.split('\n')
                    logger.info("zpool get all : {}".format(output))
                    zpool_property, bootpool, bootpath = self.property_parser(sp_output)
                    zpool_propertys.append({'propertykind': 'zpool', 'dataset': dataset, 'zpool': zpool_name, 'zfstype': zfstype, 'propertys': zpool_property})

        except Exception as e:
            logger.info("[collect_zfsproperty] EXCEPT : {}".format(e))
        return propertys, zpool_propertys, bootpool, bootpath

    def collect_zdb(self):
        poollist = None
        try:
            stdout = ZFS.zdb_list_grep()
            line = stdout.split('\n')
            poollist = self.zdb_parser(line)
        except Exception as e:
            logger.info("[searchvolumedataset] EXCEPT : {}".format(e))

        return poollist

    def collect_disk_dev(self, osname):
        devicelist = []
        bootdevname = None
        if osname.__eq__('FreeBSD'):
            logger.info("Enter FreeBSD")
            try:
                stdout = ZFS.dev_list_freebsd()
                line = stdout.split('\n')
                logger.info('devicelist stdout : {}'.format(line))
                for raw in line:
                    values = raw.split(':')
                    if len(values) > 1:
                        devicelist.append(values[1].strip())

            except Exception as e:
                logger.info("Exception Collect Disk Device : {}".format(e))
            logger.info('devicelist : {}'.format(devicelist))
        else:
            try:
                stdout = ZFS.dev_list_linux()
                line = stdout.split('\n')
                logger.info('devicelist stdout : {}'.format(line))
                for raw in line:
                    value = raw.strip()
                    if not value.__eq__(''):
                        devicelist.append(value)
            except Exception as e:
                logger.info("Exception Collect Disk Device : {}".format(e))
            logger.info('devicelist : {}'.format(devicelist))

            for devname in devicelist:
                try:
                    dev_path = "/dev/{}".format(devname)
                    stdout = ZFS.dev_boot_linux(dev_path)
                    line = stdout.split('/n')
                    tmp_devname = None
                    for raw in line:
                        tmp = raw.split(' ')
                        if not tmp[0].__eq__(''):
                            tmp_devname = tmp[0]

                        if tmp_devname is not None:
                            if bootdevname is None:
                                bootdevname = tmp_devname
                            else:
                                bootdevname += ','+tmp_devname
                except Exception as e:
                    logger.info("Exception Find Boot Device : {}".format(e))
                logger.info('bootdevname : {}'.format(bootdevname))
        return bootdevname, devicelist


    def collect_zpool_status(self, poollist):
        try:
            for pooldata in poollist:
                pool_name = pooldata.get('pool')
                print_cnt = 1
                print_cnt += pooldata.get('disk_total_cnt') + pooldata.get('print_cnt')
                if platform.system() == 'FreeBSD':
                    stdout = ZFS.zpool_status_grep_freebsd(pool_name, print_cnt)
                else:
                    stdout = ZFS.zpool_status_grep(pool_name, print_cnt)
                line =stdout.split('\n')
                create_option = self.status_parser(line)
                pooldata['create_option'] = 'zpool create -f ' + create_option
        except Exception as e:
            logger.info("[searchvolumedataset] EXCEPT : {}".format(e))


    def collect_zfs(self):
        cur_propertys = []
        target_datasetlist = []
        boot_pool = None
        boot_path = None
        if platform.system() == 'FreeBSD':
            osname = 'FreeBSD'
        else:
            osname = 'Linux'
        # Search DataSet
        datasetlist_fs, cnt_fs = self.searchdataset('filesystem')
        for pool, dataset in datasetlist_fs:
            target_datasetlist.append((pool, dataset))

        if cnt_fs > 0:
            # FileSystem Property
            propertys, zpool_propertys, bootpool, bootpath = self.collect_zfsproperty(datasetlist_fs, 'filesystem')
            cur_propertys.append({'zfs_property': propertys, 'zpool_property': zpool_propertys})
            if bootpool is not None:
                boot_pool = bootpool
                boot_path = bootpath
        datasetlist_vol, cnt_vol = self.searchdataset('volume')
        for pool, dataset in datasetlist_vol:
            target_datasetlist.append((pool, dataset))

        if cnt_vol > 0:
            # Volume Property
            propertys, zpool_propertys, bootpool, bootpath = self.collect_zfsproperty(datasetlist_vol, 'volume')
            cur_propertys.append({'zfs_property': propertys, 'zpool_property': zpool_propertys})
            if bootpool is not None:
                boot_pool = bootpool
                boot_path = bootpath
        logger.info("[collect_zfs] current propertys : {}".format(cur_propertys))
        snaplist, snap_cnt = self.collect_zfssnapshotlist()
        poollist = self.collect_zdb()
        self.collect_zpool_status(poollist)
        boot_devname, devlist = self.collect_disk_dev(osname)
        logger.info("[collect_zfs] pool list : {}".format(poollist))
        # {'propertykind': 'zpool or zfs', 'dataset': dataset, 'zpool': zpool_name, 'zfstype': zfstype,
        # 'propertys': zpool_property}

        return {'cur_property': cur_propertys, 'cur_snaplist': snaplist, 'cur_poollist':poollist,
                'cur_boot_pool': boot_pool, 'cur_boot_path': boot_path, 'target_datasetlist': target_datasetlist,
                'cur_boot_devname': boot_devname, 'cur_devlist': devlist, 'osname': osname}

    def cur_snaplist(self, isall=False):
        snaplist, snap_cnt = self.collect_zfssnapshotlist(isall)
        return snaplist, snap_cnt


    def save_partitioninfo(self, osname, devlist, save_path):
        if osname.__eq__('FreeBSD'):
            islinux = False
        else:
            islinux = True

        for devname in devlist:
            if islinux:
                dev_path = "/dev/{}".format(devname)
                savepath = "{}/{}".format(save_path, devname)
                try:
                    ZFS.dev_partition_dump_linux(dev_path, savepath)
                except Exception as e:
                    logger.info("[save_partitioninfo] Exception : {}".format(e))
            else:
                try:
                    savepath = "{}/{}".format(save_path, devname)
                    ZFS.gpart_backup_local(devname, savepath)
                except Exception as e:
                    logger.info("[save_partitioninfo] Exception : {}".format(e))

    def check_zfssnapshotlist(self, isall=False):
        result = None
        line_cnt = -1
        try:
            stdout = ZFS.zfs_list(target=None, zfs_types=["snapshot"])
            line = stdout.split()
            result, line_cnt = self.zfslist_parser(line, True, self.volume_name, isall)
            logger.info("zfs snapshot list count : {}".format(line_cnt))
            logger.info("zfs snapshot list data : {}".format(result))
        except Exception as e:
            logger.info("[collect_zfslist] EXCEPT : {}".format(e))

        return result, line_cnt



