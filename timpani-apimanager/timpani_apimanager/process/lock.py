import logging

class ProcessLock(object):
    logger = logging.getLogger(__name__)

    spin_lock = []

    # target : server uuid
    def setlock(self, target_uuid):

        if target_uuid is None:
            self.logger.info("TARGET UUID NONE")
            return False

        isNotUUID = True
        for uuid in self.spin_lock:
            if target_uuid.upper().__eq__(uuid.upper()):
                isNotUUID = False
                break
        if isNotUUID:
            self.spin_lock.append(target_uuid)
            return True
        else:
            return False

    def unsetlock(self, target_uuid):
        if target_uuid is None:
            self.logger.info("TARGET UUID NONE")
            return False

        isNotUUID = True
        for uuid in self.spin_lock:
            if target_uuid.upper().__eq__(uuid.upper()):
                isNotUUID = False
                break
        if isNotUUID:
            return False
        else:
            self.spin_lock.remove(target_uuid)
            return True