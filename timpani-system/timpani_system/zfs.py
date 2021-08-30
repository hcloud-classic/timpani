import subprocess
import os
import platform
from .command import _Command

import timpani_system.check
#import timpani_system.utility
import timpani_system.system.agnostic


class ZFS(object):
    @staticmethod
    def zpool_set(pool: str, prop: str) -> str:
        """
        zpool set property=value pool
                 Sets the given property on the specified pool.  See the
                 Properties section for more information on what properties
                 can be set and acceptable values.
        """
        if pool is None:
            raise TypeError("Target name cannot be of type 'None'")

        command = _Command("set", [],
                       main_command="zpool",
                       targets=[prop, pool])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to set pool property {prop}\n{e.output}\n")

    @staticmethod
    def zpool_get(pool: str = None,
              scripting: bool = True,
              properties: list = None,
              columns: list = None,
              parsable: bool = False) -> str:
        """
         zpool get [-Hp] [-o field[,field]...] all|property[,property]...
             pool...
             Retrieves the given list of properties (or all properties if
             all is used) for the specified storage pool(s).  These prop‐
             erties are displayed with the following fields:
                     name          Name of storage pool
                     property      Property name
                     value         Property value
                     source        Property source, either 'default' or 'local'.
             See the Properties section for more information on the avail‐
             able pool properties.
             -H      Scripted mode.  Do not display headers, and separate
                     fields by a single tab instead of arbitrary space.
             -o field
                     A comma-separated list of columns to display.
                     name,property,value,source is the default value.
             -p      Display numbers in parsable (exact) values.
        NOTE: -o requires zfsonlinux 0.7.0
        https://github.com/zfsonlinux/zfs/commit/2a8b84b747cb27a175aa3a45b8cdb293cde31886
        """
        call_args = []

        if scripting:
            call_args.append("-H")
        if parsable:
            call_args.append("-p")
        if properties is None:
            property_target = "all"
        elif properties:
            if "all" in properties:
                if len(properties) < 2:
                    property_target = "all"
                else:
                    raise RuntimeError("Cannot use 'all' with other properties")
            else:
                property_target = ",".join(properties)
        else:
            raise RuntimeError("Cannot request no property type")
        target_list = [property_target]
        if pool is not None:
            target_list.append(pool)
        command = _Command("get", call_args,
                           main_command="zpool",
                           targets=target_list)
        command.argcheck_columns(columns)
        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs property '{property_target}' "
                               "from {pool}\n{e.output}\n")

    @staticmethod
    def geom_list(properties: list = None):
        call_args = []
        if properties is None:
            property_target = "list"
        target_list = [property_target]
        command = _Command("disk", call_args,
                           main_command="geom",
                           targets=target_list)
        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs property '{property_target}' "
                               "from {pool}\n{e.output}\n")

    @staticmethod
    def zdb_list():
        try:
            return _Command.shell_run('zdb')
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs property '{property_target}' "
                               "from {pool}\n{e.output}\n")

    # return : is_zfs, is_lvm
    @staticmethod
    def check_zfs():
        if platform.system() == 'FreeBDS':
            return True

        try:
            out = _Command.shell_run('lsblk -o FSTYPE | grep zfs | wc -l')
            if int(out) > 0:
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get ZFS Type")

    @staticmethod
    def check_backup_target():
        if platform.system() == 'FreeBDS':
            return None

        try:
            output = _Command.shell_run("lsblk -o KNAME,FSTYPE,MOUNTPOINT -J | awk '!/zfs|swap|squashfs/'")
            return output
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get ZFS Type")

    @staticmethod
    def check_user_home():
        if platform.system() == 'FreeBDS':
            return None

        try:
            output = _Command.shell_run("tree -d -L 1 -J /home")
            return output
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get ZFS Type")


    @staticmethod
    def zpool_list(target: str = None,
                 scripting: bool = True,
                 parsable: bool = False,
                 verbose: bool = False,
                 env_variables_override: dict = None) -> str:
        """
        zpool list [-gHLPv] [-o property[,...]] [-T d|u] [pool] ... [interval [count]]

        """

        call_args = []

        if scripting:
            call_args.append("-H")

        if parsable:
            call_args.append("-p")

        if verbose:
            call_args.append("-v")

        if target is None:
            targets = []
        else:
            targets = [target]

        command = _Command("list", call_args, main_command="zpool", targets=targets,
                           env_variables_override=env_variables_override)
        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs list of {target}\n{e.output}\n")

    @staticmethod
    def zfs_create_dataset(filesystem: str,
                       create_parent: bool = False,
                       mounted: bool = True,
                       properties: list = None) -> str:
        """
        zfs create	[-pu] [-o property=value]... filesystem
        """
        if filesystem is None:
            raise TypeError("Filesystem name cannot be of type 'None'")

        call_args = []
        if create_parent:
            call_args.append('-p')

        if not mounted:
            if timpani_system.check.check_valid_system() == "freebsd":
                call_args.append('-u')
            else:
                raise SystemError("-u is not valid on this system")

        create = _Command("create", call_args, properties=properties, targets=[filesystem])

        try:
           return create.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to create {filesystem}\n{e.output}\n")

    @staticmethod
    def zfs_create_zvol(volume: str,
                    size: int,
                    size_suffix: str = "G",
                    blocksize: int = None,
                    create_parent: bool = False,
                    sparse: bool = False,
                    properties: list = None) -> str:
        """
         zfs create	[-ps] [-b blocksize] [-o property=value]... -V size volume
        """
        if volume is None:
            raise TypeError("Filesystem name cannot be of type 'None'")

        call_args = []

        if create_parent:
            call_args = ["-p"]

        if sparse:
            call_args.append('-s')

        if blocksize:
            call_args.extend(['-b', str(blocksize)])

        call_args.extend(['-V', "{str(size)}{size_suffix}"])

        command = _Command("create", call_args, properties=properties, targets=[volume])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to create {volume}\n{e.output}\n")

    @staticmethod
    def zfs_clone(snapname: str,
              filesystem: str,
              properties: list = None,
              create_parent: bool = False) -> str:

        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if create_parent:
            call_args = ["-p"]

        command = _Command("clone", call_args, properties=properties, targets=[snapname, filesystem])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to clone {filesystem}\n{e.output}\n")

    @staticmethod
    def zfs_snapshot(filesystem: str,
                 snapname: str,
                 recursive: bool = False,
                 properties: list = None) -> str:
        """
         zfs snapshot|snap [-r] [-o	property=value]...
         filesystem@snapname|volume@snapname
         filesystem@snapname|volume@snapname...
        """
        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if recursive:
            call_args = ["-r"]

        command = _Command("snapshot", call_args,
                           properties=properties, targets=["{filesystem}@{snapname}".format(filesystem=filesystem, snapname=snapname)])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to snapshot {filesystem}\n{e.output}\n")

    @staticmethod
    def zfs_send(send_target: str,
                    target_host: str,
                    isfull: bool = False,
                    isgzip: bool = True,
                    remote_path: list = None) -> str:

        if isfull:
            zfs_cmd = "zfs send -Rv {send_target} | ".format(send_target=send_target)
        else:
            zfs_cmd = "zfs send {send_target} | ".format(send_target=send_target)

        if isgzip:
            gzip_cmd = "gzip | "
            ssh_cmd = "ssh {target_host} \"cat > {remote_path}.zfs.gz\"".format(target_host=target_host,
                                                                                remote_path=remote_path)
            shell_cmd = zfs_cmd + gzip_cmd + ssh_cmd
        else:
            ssh_cmd = "ssh {target_host} \"cat > {remote_path}.zfs\"".format(target_host=target_host,
                                                                             remote_path=remote_path)
            shell_cmd = zfs_cmd + ssh_cmd

        try:
            _Command.shell_run(shell_cmd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to snapshot {filesystem}\n{e.output}\n")

    @staticmethod
    def zpool_status():
        shell_cmd = "zpool status -L | awk '{print $1}'"
        try:
            output =  _Command.shell_run(shell_cmd)
            print("output : {}".format(output))
            return output
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs list of {target}\n{e.output}\n")

    @staticmethod
    def gpart_backup():
        if platform.system() == 'FreeBDS':
            shell_cmd = "gpart backup"
        else:
            return None

        try:
            return _Command.shell_run(shell_cmd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs list of {target}\n{e.output}\n")

    @staticmethod
    def timpani_checksum(dataset:str) -> str:
        target = "/{dataset}/.test_checksum_timpani".format(dataset=dataset)
        if platform.system() == 'FreeBDS':
            shell_cmd = "md5 {}".format(target)
        else:
            shell_cmd = "md5sum {}".format(target)
        try:
            return _Command.shell_run(shell_cmd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs list of {target}\n{e.output}\n")

    @staticmethod
    def timpani_checksum_testfile_create(dataset: str) -> str:
        test_file_path = "/{dataset}/.test_checksum_timpani".format(dataset=dataset)
        shell_cmd = "truncate -s 1024000 {file_path}".format(file_path=test_file_path)

        try:
            _Command.shell_run(shell_cmd)
            if os.path.isfile(test_file_path):
                return ZFS.timpani_checksum(dataset)
            else:
                return None

        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to snapshot {filesystem}\n{e.output}\n")

    @staticmethod
    def zfs_get(target: str = None,
            recursive: bool = False,
            depth: int = None,
            scripting: bool = True,
            parsable: bool = False,
            columns: list = None,
            zfs_types: list = None,
            source: list = None,
            properties: list = None,
            env_variables_override: dict = None) -> str:
        """
         zfs get [-r|-d depth] [-Hp] [-o all | field[,field]...] [-t
         type[,type]...] [-s source[,source]...] all | property[,property]...
         filesystem|volume|snapshot...
        """

        call_args = []

        if recursive:
            call_args.append("-r")

        if scripting:
            call_args.append("-H")

        if parsable:
            call_args.append("-p")

        if zfs_types:
            call_args.extend(["-t", ",".join(zfs_types)])

        if source:
            call_args.extend(["-s", ",".join(source)])

        if properties is None:
            property_target = "all"
        elif properties:
            if "all" in properties:
                if len(properties) < 2:
                    property_target = "all"
                else:
                    raise RuntimeError("Cannot use 'all' with other properties")
            else:
                property_target = ",".join(properties)
        else:
            raise RuntimeError("Cannot request no property type")
        if target is None:
            command = _Command("get", call_args, targets=[property_target],
                               env_variables_override=env_variables_override)
        else:
            command = _Command("get", call_args, targets=[property_target, target],
                       env_variables_override=env_variables_override)

        command.argcheck_depth(depth)
        command.argcheck_columns(columns)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs properties of {target}\n{e.output}\n")

    @staticmethod
    def zfs_list(target: str = None,
             recursive: bool = False,
             depth: int = None,
             scripting: bool = True,
             parsable: bool = False,
             columns: list = None,
             zfs_types: list = None,
             sort_properties_ascending: list = None,
             sort_properties_descending: list = None,
             env_variables_override: dict = None) -> str:
        """
        zfs list [-r|-d depth] [-Hp] [-o property[,property]...] [-t
        type[,type]...] [-s property]... [-S property]...
        filesystem|volume|snapshot...
        """

        call_args = []

        if recursive:
            call_args.append("-r")

        if scripting:
            call_args.append("-H")

        if parsable:
            call_args.append("-p")

        if zfs_types:
            call_args.extend(["-t", ",".join(zfs_types)])

        if sort_properties_ascending is not None:
            call_args.extend(
                [p for prop in sort_properties_ascending for p in ("-s", prop)])

        if sort_properties_descending is not None:
            call_args.extend(
                [p for prop in sort_properties_descending for p in ("-S", prop)])

        if target is None:
            targets = []
        else:
            targets = [target]

        command = _Command("list", call_args, targets=targets,
                           env_variables_override=env_variables_override)
        command.argcheck_depth(depth)
        command.argcheck_columns(columns)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to get zfs list of {target}\n{e.output}\n")

    @staticmethod
    def zfs_destroy(target: str,
                recursive_children: bool = False,
                recursive_dependents: bool = False,
                force_unmount: bool = False,
                dry_run: bool = False,
                machine_parsable: bool = False,
                verbose: bool = False) -> str:
        """
        zfs destroy [-fnpRrv] filesystem|volume
        """
        if target is None:
            raise TypeError("Target name cannot be of type 'None'")

        call_args = []

        if recursive_children:
            call_args.append("-r")
        if recursive_dependents:
            call_args.append("-R")
        if force_unmount:
            call_args.append("-")
        if dry_run:
            call_args.append("-n")
        if machine_parsable:
            call_args.append("-p")
        if verbose:
            call_args.append("-v")

        command = _Command("destroy", call_args, targets=[target])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to destroy {target}\n{e.output}\n")


    @staticmethod
    def zfs_destroy_snapshot(snapname: str,
                         recursive_descendents: bool = False,
                         recursive_clones: bool = False,
                         dry_run: bool = False,
                         machine_parsable: bool = False,
                         verbose: bool = False,
                         defer: bool = False) -> str:
        """
        zfs destroy [-dnpRrv] snapshot[%snapname][,...]
        """
        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if recursive_descendents:
            call_args.append("-r")
        if recursive_clones:
            call_args.append("-R")
        if dry_run:
            call_args.append("-n")
        if machine_parsable:
            call_args.append("-p")
        if verbose:
            call_args.append("-v")
        if defer:
            call_args.append("-d")

        command = _Command("destroy", call_args, targets=[snapname])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to destroy {snapname}\n{e.output}\n")

    @staticmethod
    def zfs_rollback(snapname: str,
                 destroy_between: bool = False,
                 destroy_more_recent: bool = False,
                 force_unmount: bool = False):
        """
         zfs rollback [-rRf] snapshot
        """
        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if destroy_between:
            call_args.append("-r")
        if destroy_more_recent:
            call_args.append("-R")
        if force_unmount:
            call_args.append("-")

        command = _Command("rollback", call_args, targets=[snapname])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to rollback {snapname}\n{e.output}\n")

    @staticmethod
    def zfs_promote(clone: str) -> str:
        """
        zfs promote clone-filesystem
        """
        command = _Command("promote", [], targets=[clone])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to promote {clone}\n{e.output}\n")

    @staticmethod
    def zfs_rename(target_source: str,
               target_dest: str,
               create_parents: bool = False,
               dont_remount: bool = False,
               force_unmount: bool = False,
               recursive: bool = False) -> str:
        """
         zfs rename	[-f] filesystem|volume|snapshot	filesystem|volume|snapshot
         zfs rename	[-f] -p	filesystem|volume filesystem|volume
         zfs rename	-u [-p]	filesystem filesystem
         zfs rename	-r snapshot snapshot
        """
        if target_source is None or target_dest is None:
            raise TypeError("Target name cannot be of type 'None'")

        call_args = []

        if create_parents:
            call_args.append("-p")

        if dont_remount:
            call_args.append("-u")

        if force_unmount:
            call_args.append("-")

        if recursive:
            call_args.append("-r")

        command = _Command("rename", call_args, targets=[target_source, target_dest])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to rename {target_source} to {target_dest}\n{e.output}\n")

    @staticmethod
    def zfs_set(target: str, prop: str) -> str:
        """
        zfs set property=value [property=value]...	filesystem|volume|snapshot
        """
        if target is None:
            raise TypeError("Target name cannot be of type 'None'")

        command = _Command("set", [], targets=[prop, target])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to \n{e.output}\n")


    @staticmethod
    def zfs_inherit(prop: str,
                target: str,
                recursive: bool = False,
                revert: bool = False) -> str:
        """
        zfs inherit [-rS] property	filesystem|volume|snapshot...
        """
        if prop is None:
            raise TypeError("Property name cannot be of type 'None'")

        if target is None:
            raise TypeError("Target name cannot be of type 'None'")

        call_args = []

        if recursive:
            call_args.append("-r")

        if revert:
            call_args.append("-S")

        command = _Command("inherit", call_args, targets=[prop, target])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to inherit property\n{e.output}\n")

    @staticmethod
    def zfs_upgrade_list(supported: bool = False) -> str:
        """
        zfs upgrade [-v]
        Displays a list of file systems that are not the most recent version.
        -v	 Displays ZFS filesystem versions supported by the current
             software. The current ZFS filesystem version and all previous
            supported versions are	displayed, along with an explanation
            of the	features provided with each version.
        """
        call_args = []
        if supported:
            call_args.append("-v")

        command = _Command("upgrade", call_args)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to list upgradeable filesystems\n{e.output}\n")

    @staticmethod
    def zfs_upgrade(target: str = None,
                descendent: bool = False,
                version: str = None,
                upgrade_all: bool = False) -> str:
        """
        zfs upgrade [-r] [-V version] -a |	filesystem
        """
        if target is not None and upgrade_all:
            raise RuntimeError("Both target and upgrade all cannot be true")

        call_args = []

        if descendent:
            call_args.append("-r")

        if upgrade_all:
            call_args.append("-a")

        if version is not None:
            call_args.extend(["-V", version])

        targets = [target] if target is not None else []

        command = _Command("upgrade", call_args, targets=targets)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to run upgrade\n{e.output}\n")

    @staticmethod
    def zfs_mount_list() -> str:
        """
         zfs mount
         Displays all ZFS file systems currently mounted.
        """

        command = _Command("mount", [])

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to \n{e.output}\n")

    @staticmethod
    def zfs_mount(target: str = None,
              progress: bool = False,
              overlay: bool = False,
              properties: list = None,
              mount_all: bool = False) -> str:
        """
         zfs mount [-vO] [-o property[,property]...] -a | filesystem
        """
        if target is not None and mount_all:
            raise RuntimeError("Both target and unmount all cannot be true")

        call_args = []

        if progress:
            call_args.append("-v")

        if overlay:
            call_args.append("-O")

        if mount_all:
            call_args.append("-a")

        if properties:
            call_args.extend(["-o", ",".join(properties)])

        targets = [target] if target is not None else []

        command = _Command("mount", call_args, targets=targets)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to mount target\n{e.output}\n")


    @staticmethod
    def zfs_unmount(target: str = None,
                force: bool = False,
                unmount_all: bool = False) -> str:
        """
         zfs unmount|umount	[-f] -a	| filesystem|mountpoint
        """
        if target is not None and unmount_all:
            raise RuntimeError("Both target and unmount all cannot be true")

        call_args = []

        if force:
            call_args.append("-")

        if unmount_all:
            call_args.append("-a")

        targets = [target] if target is not None else []

        command = _Command("unmount", call_args, targets=targets)

        try:
            return command.run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to unmount {target}\n{e.output}\n")

