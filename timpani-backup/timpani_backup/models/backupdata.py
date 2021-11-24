class BackupData(object):
    snap_target = None
    snapname = None
    parent_snapshot = None
    backup_host = None
    remote_path = None
    run_uuid = None
    action_kind = None
    dataset_name = None
    gpart_remote_path = None

    def __init__(self, snap_target=None, snapname=None, parent_snapshot=None, backup_host=None,
                 remote_path=None,
                 run_uuid=None, action_kind=None, dataset_name = None, gpart_remote_path=None):
        self.snap_target = snap_target
        self.snapname=snapname
        self.parent_snapshot = parent_snapshot
        self.backup_host = backup_host
        self.remote_path = remote_path
        self.run_uuid = run_uuid
        self.action_kind = action_kind
        self.dataset_name = dataset_name
        self.gpart_remote_path = gpart_remote_path

    def __str__(self):
        return str(self.__dict__)