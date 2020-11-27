"""ZFS library"""

from typing import Optional

from timpani_system.zfs import ZFS

"""
ZFS helper functions
"""


def is_snapshot(snapname: str) -> bool:
    if "@" in snapname:
        return dataset_exists(snapname, zfs_type="snapshot")

    return False


"""
Check if clone, raise if not valid dataset
"""


def is_clone(dataset: str) -> bool:
    try:
        origin = ZFS.zfs_get(dataset,
                                       properties=["origin"],
                                       columns=["value"])
    except RuntimeError:
        raise

    if origin.split()[0] == "-":
        return False

    return True


def dataset_parent(dataset: str) -> Optional[str]:
    if dataset is None:
        raise TypeError

    try:
        cmd.zfs_list(dataset)
    except RuntimeError:
        return None

    return dataset.rsplit('/', 1)[0]


def dataset_child_name(dataset: str, check_exists: bool = True) -> Optional[str]:
    if dataset is None:
        raise TypeError

    if check_exists:
        try:
            cmd.zfs_list(dataset)
        except RuntimeError:
            return None

    return dataset.rsplit('/', 1)[-1]


def snapshot_parent_dataset(snapshot: str) -> Optional[str]:
    """
    Given a snapshot find the parent dataset
    """
    if snapshot is None:
        raise TypeError

    if not ("@" in snapshot):
        return None

    try:
        cmd.zfs_list(snapshot, zfs_types=["snapshot"])
    except RuntimeError:
        return None

    return snapshot.rsplit('@', 1)[-2]


def dataset_exists(target: str, zfs_type: str = "filesystem") -> bool:
    if target is None:
        raise TypeError

    try:
        cmd.zfs_list(target, zfs_types=[zfs_type])
    except RuntimeError:
        return False

    return True