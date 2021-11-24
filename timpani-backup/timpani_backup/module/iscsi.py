import logging
import datetime
import re
import platform
import subprocess
import xml.etree.ElementTree as elemTree

from ..util.systemutil import Systemutil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class IscsiProc(object):

    def run(self, cmd):

        try:
            process = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            returncode = process.wait()
        except subprocess.CalledProcessError as e:
            raise e

        return process.stdout.read()

    def iscsiinfo(self, data):
        iscsiinfo = []
        server_uuid = data.get('server_uuid')
        target_uuid = data.get('target_uuid')
        try:
            cmd = "ctladm devlist -x"
            stdout = self.run(cmd)

            tree = elemTree.fromstring(stdout)
            iter_e = tree.iter(tag="lun")
            for lundata in iter_e:
                lun_id = lundata.attrib.get('id')
                backend_type = lundata.find("backend_type").text
                lun_type = lundata.find("lun_type").text
                size = lundata.find("size").text
                blocksize = lundata.find("blocksize").text
                serial_number = lundata.find("serial_number").text
                device_id = lundata.find("device_id").text
                num_threads = lundata.find("num_threads").text
                file_path = lundata.find("file").text
                ctld_name = lundata.find("ctld_name").text
                scsiname = lundata.find("scsiname").text
                save_data = {'lun_id': lun_id,
                             'backend_type': backend_type,
                             'lun_type': lun_type,
                             'size': size,
                             'blocksize': blocksize,
                             'serial_number': serial_number,
                             'device_id': device_id,
                             'num_threads': num_threads,
                             'file_path': file_path,
                             'ctld_name': ctld_name,
                             'scsiname': scsiname,
                             'server_uuid': server_uuid,
                             'target_uuid': target_uuid
                             }
                iscsiinfo.append(save_data)

        except Exception as e:
            print("Exception : {}".format(e))
            iscsiinfo = []

        data['iscsiinfo'] = iscsiinfo
        return data

    def demoncheck(self):
        isrunning = False
        if platform.system() == 'FreeBSD':
            try:
                cmd = "service ctld status"
                stdout = self.run(cmd)
                if 'as pid' in stdout:
                    isrunning = True
            except Exception as e:
                errcode = '4020'
                errstr = 'SnapShot File Transfer Failed'
        return isrunning

    def iscsilunremove(self, data):
        iscsiinfolist = data.get('iscsiinfo')
        dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
        for iscsiinfo in iscsiinfolist:
            file_path = iscsiinfo.get('file_path')
            if dataset in file_path:
                lun_id = iscsiinfo.get('lun_id')
                backend = iscsiinfo.get('backend_type')
                data['remove_iscsiinfo'] = iscsiinfo
                break

        try:
            cmd = "ctladm remove -b {backend} -l {lun_id}".format(backend=backend, lun_id=lun_id)
            stdout = self.run(cmd)
            logger.info("[iscsilunremove] run stdout : {}".format(stdout))
        except Exception as e:
            logger.info("iscsilunremove Failed")

        return data

    def iscsilunadd(self, data):
        remove_iscsiinfo = data.get('remove_iscsiinfo')
        if remove_iscsiinfo is None:
            return data

        lun_id = remove_iscsiinfo.get('lun_id')
        backend_type = remove_iscsiinfo.get("backend_type")
        lun_type = remove_iscsiinfo.get("lun_type")
        size = remove_iscsiinfo.get("size")
        blocksize = remove_iscsiinfo.get("blocksize")
        serial_number = remove_iscsiinfo.get("serial_number")
        device_id = remove_iscsiinfo.get("device_id")
        num_threads = remove_iscsiinfo.get("num_threads")
        file_path = remove_iscsiinfo.get("file_path")
        ctld_name = remove_iscsiinfo.get("ctld_name")
        scsiname = remove_iscsiinfo.get("scsiname")

        bs_size = int(blocksize) * int(size)

        try:
            cmd = "ctladm create -b {backend} -B {blocksize} -d {device_id} " \
                  "-l {lun_id} -s {size} -S {serial} -o file={file_path} -o ctld_name={ctld_name} " \
                  "-o scsiname={scsiname}".format(backend=backend_type, blocksize=blocksize, device_id=device_id,
                                                  lun_id=lun_id, size=bs_size, serial=serial_number, file_path=file_path,
                                                  ctld_name=ctld_name, scsiname=scsiname)
            stdout = self.run(cmd)
            logger.info("[iscsilunadd] run stdout : {}".format(stdout))
        except Exception as e:
            logger.info("iscsilunadd Failed")


        return data


