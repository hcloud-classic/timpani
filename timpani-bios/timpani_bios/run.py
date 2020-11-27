from .syscfg.biosconfig import BiosConfig

def test():
    print("[INIT] Send BIOS Configuration Info")
    bios = BiosConfig()
    bios_config_info = bios.read_syscfg("test_syscfg.INI")
    print(bios_config_info)

if __name__=="__main__":
    test()
