#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        databaseCreater.py
#
# Purpose:     This module is used to create/add the gateway node and the current
#              running state info in to the database.
#
# Author:      Yuancheng Liu
#
# Created:     2021/12/07
# Version:     v_0.2
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os
import json
import time
import random
import sqlite3
from sqlite3 import Error
import ConfigLoader as cl 
import globalVal as gv

print("Current working directory is : %s" % os.getcwd())
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)
GV_FLG = True  # Flag to identify whether use global value

DB_PATH = gv.DB_PATH if GV_FLG else os.path.join(dirpath , "node_database.db")
NODES_FILE = gv.NODES_FILE if GV_FLG else  os.path.join(dirpath, 'NodesRcd.txt')

# gateway information table query.
gwInfoTable = "CREATE TABLE IF NOT EXISTS gatewayInfo(id integer PRIMARY KEY,\
                                                                name text NOT NULL,\
                                                                ipAddr text NOT NULL,\
                                                                lat float NOT NULL,\
                                                                lng float NOT NULL,\
                                                                actF integer NOT NULL,\
                                                                rptTo integer NOT NULL,\
                                                                type text NOT NULL)"
# gateway current state table query.
gwStateTable = "CREATE TABLE IF NOT EXISTS gatewayState(time float PRIMARY KEY,\
                                                                 id text NOT NULL,\
                                                                 updateInfo text NOT NULL)"

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class databaseCreater(object):

    """ Download the webpage screen shot base on the input url."""
    def __init__(self, dataBasePath):
        try:
            # Create a connection with the database
            self.connection = sqlite3.connect(dataBasePath)
            print("Connection is established: Database is created in node_database.db")
            self.cursorObj = self.connection.cursor() # Cursor can be used to call execute method for SQL queries
            self.cfgLoader = cl.ConfigLoader(NODES_FILE, mode='r', filterChars=('#', '', '\n'))
        except Error: print("__init__ error: %s" %str(Error))

#-----------------------------------------------------------------------------
    def createTables(self):
        """ Ceate the node info and state table. """
        try:
            self.cursorObj.execute(gwInfoTable)
            self.connection.commit()
            self.cursorObj.execute(gwStateTable)
            self.connection.commit()
            for val in self.cfgLoader.getJson().values():
                node = json.loads(val)
                insertQuery = 'INSERT INTO gatewayInfo VALUES({}, "{}", "{}", {}, {}, {}, {}, "{}")'.\
                    format(node["no"], node["name"], node["ipAddr"], node["lat"], node["lng"],\
                         node["actF"], node["rptTo"], node["type"])
                self.cursorObj.execute(insertQuery)
                self.connection.commit()
        except Error: print("createTables error: %s" %str(Error))

#-----------------------------------------------------------------------------
    def clearStateTable(self):
        self.cursorObj.execute('DELETE FROM gatewayState')
        self.connection.commit()

#-----------------------------------------------------------------------------
    def updateStateTable(self, gatewayID, infoStr):
        """ insert gateway state info in to the state table
        Args:
            gatewayID ([int]): gateway ID
            infoStr ([json/dict]): state dict. Example: {"comTo": [2], "throughputIn": 0, "throughputOut": 0, "actF": 0}
        """
        insertQuery = "INSERT INTO gatewayState(time, id, updateInfo) VALUES({}, '{}', '{}')".\
                        format(time.time(), str(gatewayID), json.dumps(infoStr))
        self.cursorObj.execute(insertQuery)
        self.connection.commit()
        time.sleep(1) # optional

#-----------------------------------------------------------------------------
    def closeConnection(self):
        print("Closing database connection")
        self.connection.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def getRandomStateInfo():
    """ Create a random state info json.
    Returns:
        id, state Dict.
    """
    gwID = random.randrange(5)
    id_information = {}
    actF_status = 0 if random.random() < 0.3 else 1
    comTo_list = [i for i in range(5)] # Create a list with all the nodes
    comTo_list = random.sample(comTo_list, k=random.randrange(4))
    #if 0 in comTo_list: comTo_list.remove(0)
    #if 4 in comTo_list: comTo_list.remove(4)
    if gwID in comTo_list: comTo_list.remove(gwID)
    # Fill up the id information for that node
    id_information['comTo'] = comTo_list
    id_information['throughputIn'] = round(random.uniform(1, 10), 2) if actF_status else 0
    id_information['throughputOut'] = round(random.uniform(1, 10), 2) if actF_status else 0
    id_information['actF'] = actF_status
    return gwID, id_information

def main():
    print("Start Database Insert Simulation")
    tableCheck = os.path.exists(DB_PATH)
    connector = databaseCreater(DB_PATH)
    if not tableCheck: connector.createTables()
    connector.clearStateTable()
    #for _ in range(2):
    while True:
        id, info = getRandomStateInfo()
        print("Add info: %s" %str((id, info)))
        connector.updateStateTable(id, info)
        time.sleep(5)
    connector.closeConnection()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
