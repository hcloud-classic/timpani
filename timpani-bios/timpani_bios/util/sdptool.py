import subprocess

class SDPTool(object):


    def run(self, cmd):
        try:
            process = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, shell=True)
            returncode = process.wait()
        except subprocess.CalledProcessError as e:
            raise e

        return returncode, process.stdout.read()

    def getini(self, host, user, passwd):
        cmd = "SDPTool {host} {user} {passwd} getini -no_user_interaction".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7001"
            errmsg = "Power ON Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
            # FAILE : Set Chassis Power Control to Up / On failed: Command not supported in present state
            # SUCCESS : Chassis Power Control: Up / On
        return output

    def getbiosconfigall(self, host, user, passwd):
        #Get Bios Config ALL (Redfish Version of getini)
        cmd = "SDPTool {host} {user} {passwd} get_biosconfig_all".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7001"
            errmsg = "Power ON Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
            # FAILE : Set Chassis Power Control to Up / On failed: Command not supported in present state
            # SUCCESS : Chassis Power Control: Up / On
        return output

    def deployoptions(self, host, user, passwd, syscfg_path):
        #Deploy Options *reboot requried
        cmd = "SDPTool {host} {user} {passwd} deployoptions {syscfg_path} -no_user_interaction".format(host=host, user=user, passwd=passwd, syscfg_path=syscfg_path)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7001"
            errmsg = "Power ON Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
            # FAILE : Set Chassis Power Control to Up / On failed: Command not supported in present state
            # SUCCESS : Chassis Power Control: Up / On
        return output

    def systeminfo(self, host, user, passwd):
        #Deploy Options *reboot requried
        cmd = "SDPTool {host} {user} {passwd} systeminfo".format(host=host, user=user, passwd=passwd)
        try:

            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7001"
            errmsg = "Power ON Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
            # FAILE : Set Chassis Power Control to Up / On failed: Command not supported in present state
            # SUCCESS : Chassis Power Control: Up / On
        return output

    def sensor(self, host, user, passwd):
        #Deploy Options *reboot requried
        cmd = "SDPTool {host} {user} {passwd} sensor".format(host=host, user=user, passwd=passwd)
        cmd = cmd + "| grep \"Watts\|Minutes\" | awk '{print $1,$2,$3}'"
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7001"
            errmsg = "Power ON Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
            # FAILE : Set Chassis Power Control to Up / On failed: Command not supported in present state
            # SUCCESS : Chassis Power Control: Up / On
        return output