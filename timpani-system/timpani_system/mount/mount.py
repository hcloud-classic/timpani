import os

class SystemMount(object):
    def list_media_devices(self):
        with open("/proc/partitions","r") as f:
            devices = []

            for line in f.readlines()[2:]:  #skip header lines
                words = [ word.strip() for word in line.split() ]
                minor_number = int(words[1])
                device_name = words[3]

                if (minor_number%16) == 0:
                    path = "/sys/class/block/" + device_name

                    if os.path.islink(path):
                        if os.path.realpath(path).find("/usb") > 0:
                            devices.append("/dev/" + device_name)

            return devices

    def get_device_name(self, device):
        return os.path.basename(device)

    def get_device_block_path(self, device):
        return "/sys/block/{}".format(self.get_device_name(device))

    def get_media_path(self, device):
        return "/media/" + self.get_device_name(device)

    def get_partition(self, device):
        os.system("fdisk -l {} > output".format(device))
        with open("output", "r") as f:
            data = f.read()
            return data.split("\n")[-2].split()[0].strip()

    def is_mounted(self, device):
        return os.path.ismount(self.get_media_path(device))

    def mount_partition(self, partition, name="usb"):
        path = self.get_media_path(name)
        if not self.is_mounted(path):
            os.system("mkdir -p " + path)
            os.system("mount %s %s" % (partition, path))

    def unmount_partition(self, name="usb"):
        path = self.get_media_path(name)
        if self.is_mounted(path):
            os.system("umount " + path)
            # os.system("rm -rf " + path)

    def mount(self, device, name=None):
        if not name:
            name = self.get_device_name(device)
        self.mount_partition(self.get_partition(device), name)

    def unmount(self, device, name=None):
        if not name:
            name = self.get_device_name(device)
        self.unmount_partition(name)

    def is_removable(self, device):
        path = self.get_device_block_path(device) + "/removable"

        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip() == "1"

        return None

    def get_size(self, device):
        path = self.get_device_block_path(device) + "/size"

        if os.path.exists(path):
            with open(path, "r") as f:
                # Multiply by 512, as Linux sectors are always considered to be 512 bytes long
                # Resource: https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/include/linux/types.h?id=v4.4-rc6#n121
                return int(f.read().strip()) * 512

        return -1

    def get_model(self, device):
        path = self.get_device_block_path(device) + "/device/model"

        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def get_vendor(self, device):
        path = self.get_device_block_path(device) + "/device/vendor"

        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

