import subprocess

class IpmiTool(object):

    def run(self, cmd):

        try:
            process = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, shell=True)
            returncode = process.wait()
        except subprocess.CalledProcessError as e:
            raise e

        return returncode, process.stdout.read()

    def poweron(self, host, user, passwd):
        cmd = "ipmitool -H {host} -U {user} -P {passwd} power on".format(host=host, user=user, passwd=passwd)
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

    def powerstatus(self, host, user, passwd):
        cmd = "ipmitool -H {host} -U {user} -P {passwd} power status".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7003"
            errmsg = "Power Status Check Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
        # Chassis Power is [on/off]
        return output

    def poweroff(self, host, user, passwd):
        cmd = "ipmitool -H {host} -U {user} -P {passwd} power off".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7002"
            errmsg = "Power OFF Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
        # FAILE : Set Chassis Power Control to Down / Off failed: Command not supported in present state
        # SUCCESS : Chassis Power Control: Down / Off
        return output

    def sensor(self, host, user, passwd):
        cmd = "ipmitool -H {host} -U {user} -P {passwd} sensor".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7002"
            errmsg = "Power OFF Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
        # FAILE : Set Chassis Power Control to Down / Off failed: Command not supported in present state
        # SUCCESS : Chassis Power Control: Down / Off
        return output

    def guid(self, host, user, passwd):
        cmd = "ipmitool -H {host} -U {user} -P {passwd} mc guid".format(host=host, user=user, passwd=passwd)
        try:
            _, output = self.run(cmd)
        except subprocess.CallledProcessError as e:
            errcode = "7002"
            errmsg = "Power OFF Failed"
            res_data = {'err_code': errcode, 'err_message': errmsg}
            return res_data
        # FAILE : Set Chassis Power Control to Down / Off failed: Command not supported in present state
        # SUCCESS : Chassis Power Control: Down / Off
        return output

# IPMI_SENSOR_DATA = """
# System Airflow   | 0.000      | CFM        | ok    | na        | na        | na        | na        | na        | na
# BB Lft Rear Temp | 32.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 110.000   | 115.000   | na
# BB P1 VR Temp    | na         |            | na    | na        | 0.000     | 5.000     | 110.000   | 115.000   | na
# Front Panel Temp | 23.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 50.000    | 55.000    | 60.000
# SSB Temp         | na         |            | na    | na        | 0.000     | 5.000     | 98.000    | 103.000   | na
# BB P2 VR Temp    | na         |            | na    | na        | 0.000     | 5.000     | 110.000   | 115.000   | na
# BB BMC Temp      | 31.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 110.000   | 115.000   | na
# BB Rt Rear Temp  | 30.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 110.000   | 115.000   | na
# Riser 1 Temp     | 25.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 75.000    | 80.000    | na
# HSBP 1 Temp      | na         |            | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | na
# Exit Air Temp    | na         |            | na    | na        | 0.000     | 5.000     | 80.000    | 85.000    | na
# LAN NIC Temp     | 53.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 115.000   | 120.000   | na
# System Fan 1     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# System Fan 2     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# MTT CPU1         | na         | percent    | na    | na        | na        | na        | na        | na        | na
# System Fan 3     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# MTT CPU2         | na         | percent    | na    | na        | na        | na        | na        | na        | na
# System Fan 4     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# System Fan 5     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# System Fan 6     | na         |            | na    | na        | 1696.000  | 1961.000  | na        | na        | na
# PS1 Input Power  | 16.000     | Watts      | ok    | na        | na        | na        | 1536.000  | 1648.000  | na
# PS1 Curr Out %   | 0.000      | percent    | ok    | na        | na        | na        | 100.000   | 115.000   | na
# PS1 Temperature  | 39.000     | degrees C  | ok    | na        | na        | na        | 62.000    | 65.000    | na
# P1 Therm Ctrl %  | na         |            | na    | na        | na        | na        | 30.000    | 50.000    | na
# P2 Therm Ctrl %  | na         |            | na    | na        | na        | na        | 30.000    | 50.000    | na
# P1 DTS Therm Mgn | na         | degrees C  | na    | na        | na        | na        | 10.000    | 15.000    | na
# P2 DTS Therm Mgn | na         | degrees C  | na    | na        | na        | na        | 10.000    | 15.000    | na
# P1 Temperature   | na         | degrees C  | na    | na        | na        | na        | na        | na        | na
# P2 Temperature   | na         | degrees C  | na    | na        | na        | na        | na        | na        | na
# DIMM Thrm Mrgn 1 | na         |            | na    | na        | na        | na        | 5.000     | 10.000    | na
# DIMM Thrm Mrgn 2 | na         |            | na    | na        | na        | na        | 5.000     | 10.000    | na
# DIMM Thrm Mrgn 3 | na         |            | na    | na        | na        | na        | 5.000     | 10.000    | na
# DIMM Thrm Mrgn 4 | na         |            | na    | na        | na        | na        | 5.000     | 10.000    | na
# Agg Therm Mgn 1  | -16.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
# Agg Therm Mgn 2  | -26.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
# BB +12.0V        | na         |            | na    | na        | 10.672    | 11.002    | 13.257    | 13.642    | na
# BB +3.3V Vbat    | na         |            | na    | na        | 2.126     | 2.450     | na        | na        | na
# Pwr Unit Status  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
# IPMI Watchdog    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Physical Scrty   | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# FP NMI Diag Int  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# SMI Timeout      | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# System Event Log | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# System Event     | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Button           | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# BMC Watchdog     | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# VR Watchdog      | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Fan Redundancy   | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# SSB Therm Trip   | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# OCP Mod Presence | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# SAS Mod Presence | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# BMC FW Health    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# NM Capabilities  | 0x0        | discrete   | 0xff00| na        | na        | na        | na        | na        | na
# Fan 1 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# Fan 2 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# Fan 3 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# Fan 4 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# Fan 5 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# Fan 6 Present    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
# PS1 Status       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
# P1 Status        | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
# P2 Status        | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
# CPU ERR2         | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# CPU Missing      | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# VRD Hot          | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# PS1 Fan Fail     | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Mem P1 Thrm Trip | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Mem P2 Thrm Trip | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# Voltage Fault    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# KCS Policy       | 0x0        | discrete   | 0x0880| na        | na        | na        | na        | na        | na
# Remote Debug     | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
# HDD 0 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 1 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 2 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 3 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 4 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 5 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 6 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# HDD 7 Status     | na         | discrete   | na    | na        | na        | na        | na        | na        | na
# """


