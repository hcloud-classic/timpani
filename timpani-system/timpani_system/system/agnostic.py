import platform


def check_valid_system():
    valid_platforms = ['linux', 'freebsd']
    current_system = platform.system().lower()

    return current_system if current_system in valid_platforms else None


system = check_valid_system()

if system == "linux":
    import timpani_system.system.linux
    mountpoint_dataset = timpani_system.system.linux.mountpoint_dataset
    zfs_module_loaded = timpani_system.system.linux.zfs_module_loaded
    dataset_mountpoint = timpani_system.system.linux.dataset_mountpoint
elif system == "freebsd":
    import timpani_system.system.freebsd
    mountpoint_dataset = timpani_system.system.freebsd.mountpoint_dataset
    zfs_module_loaded = timpani_system.system.freebsd.zfs_module_loaded
    dataset_mountpoint = timpani_system.system.freebsd.dataset_mountpoint
else:
    raise SystemError("System not supported by timpani_system")