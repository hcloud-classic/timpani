import hashlib
from timpani_base.auth.ChaCha20Poly1305 import ChaCha20Poly1305
from ..config.configuration_file_reader import ConfigrationFileReader


class PasswdDecode(object):

    nonce = bytes.fromhex("000000000000000000000000")

    def __init__(self, app=None):
        config = ConfigrationFileReader()
        conf = config.read_file()
        key_str = conf['GENERAL']['SEC_KEY']
        self.app = app
        key_hex = hashlib.sha256(key_str.encode('utf-8')).hexdigest()
        self.key = bytes.fromhex(key_hex)
        if app is not None:
            app.logger.info("PASSWD KEY : {}".format(key_hex))

    def decode(self, passwd, ishex=True):
        # password : chacha20-poly1305
        # password + tag : ?? tag size : 16byte
        if self.app is not None:
            self.app.logger.info("[decode] passwd : {}".format(passwd))

        ccDec = ChaCha20Poly1305(False, self.key, self.nonce)
        str_len = len(passwd)
        decodepass = None
        if len(passwd) > 32:
            tag = passwd[str_len-32:str_len]
            decodepass = passwd[0:str_len-32]
            if self.app is not None:
                self.app.logger.info("update decodepass : {}".format(decodepass))
            res_b_pre = ccDec.update(bytes.fromhex(passwd))
            if self.app is not None:
                self.app.logger.info("passwd size : {}".format(str_len))
                self.app.logger.info("tag : {}".format(tag))
            try:
                if self.app is not None:
                    self.app.logger.info("update decodepass : {}".format(decodepass))
                res_b = ccDec.update(bytes.fromhex(decodepass))
                ccDec.verify_tag(bytes.fromhex(tag))
            except:
                # Failed TAG Check
                # if self.app is not None:
                #     self.app.logger.info("Exception E : {}".format(e))
                res_b = res_b_pre

        else:
            if self.app is not None:
                self.app.logger.info("update decodepass : {}".format(decodepass))
            res_b = ccDec.update(bytes.fromhex(passwd))


        if self.app is not None:
            self.app.logger.info("decode password byte : {}".format(res_b))
            self.app.logger.info("res_b type : {}".format(type(res_b)))

        if ishex:
            res = (res_b).hex()
        else:
            res = str(res_b, encoding='utf-8')

        if self.app is not None:
            self.app.logger.info("decodepass : {}".format(decodepass))
            self.app.logger.info("decode password : {}".format(res))
        return res


