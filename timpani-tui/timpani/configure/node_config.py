from ..constants import Constants
from dialog import Dialog

import time


class NodeConfig(object):
    def __init__(self, d, db):
        self.d = d
        self.db = db

    def add_node(self):
        code, node_info = self.d.form(
            "Insert Node Information",
            elements=Constants.ADD_NODE_INFO
        )
        if code == self.d.OK:
            if "" not in node_info:
                result = self.db.select(node_info[0])
                if not result:
                    self.db.insert(node_info)
                else:
                    self.d.infobox("There is already registered node name. Please re-check node information", title="Information")
                    time.sleep(3)
            return
        else:
            return

    def delete_node(self, node_name):
        result = self.db.select()

        if not result:
            self.d.infobox("There is no registered node.", title="Information")
            time.sleep(2)
            return
        else:
            for i in result:
                del i["ip"]
                temp_list = list(i.values())
                temp_list.append(False)
                Constants.NODE_LIST.append(tuple(temp_list))

            code, tag = self.d.radiolist(
                "Please select: ",
                choices=Constants.NODE_LIST
            )
            del Constants.NODE_LIST[:]

            if code == self.d.OK:
                if tag != "":
                    del_code = self.d.yesno(Constants.DELETE_CHECK_MSG.format(tag))
                    if del_code == self.d.OK:
                        self.db.delete(tag)
                    else:
                        return    
                return
            else:
                return
                

    def config_menu(self):
        code, tag = self.d.menu(
            "Select Action",
            choices=Constants.CONFIGURE_MENU
        )

        if code == self.d.OK:
            if tag.__eq__('1'):
                self.add_node()
            elif tag.__eq__('2'):
                self.delete_node(tag)
        elif code == self.d.CANCEL:
            return