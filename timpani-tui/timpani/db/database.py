import sqlite3


class Database:        
    
    def __init__(self, dbname=''):
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()

    def select(self, node_name=None):
        if node_name:
            sql = "SELECT * FROM `node_info` where name='{}'".format(node_name)
            self.cursor.execute(sql)
        else:
            sql = "SELECT * FROM `node_info`"
            self.cursor.execute(sql)
        result = []
        keys = ['node', 'ip', 'description']
        for i in self.cursor.fetchall():
            result.append(dict(zip(keys, i)))

        return result

    def insert(self, node_info):
        node = node_info[0]
        ip = node_info[1]
        desc = node_info[2]

        sql = "INSERT INTO node_info (name, ip, description) VALUES ('{}', '{}', '{}')".format(node, ip, desc)
        self.cursor.execute(sql)
        self.db.commit()

    def delete(self, node_name):
        sql = "DELETE FROM node_info WHERE name='{}'".format(node_name)
        self.cursor.execute(sql)
        self.db.commit()
