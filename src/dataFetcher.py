#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dataFetcher.py [python3]
#
# Purpose:     This module will work as a balancer program to load the gateway 
#              node data from data base and send the data to web host program.
#              
# Author:      Liu Yuancheng
#
# Version:     v_0.2
# Created:     2020/06/01
# Copyright:   Singtel Cyber Security Research & Development Laboratory
# License:     
#-----------------------------------------------------------------------------

# import python built in modules.
import json
import sqlite3

# import pip installed modules.
from flask import Flask, render_template, request, jsonify

# import project local modules.
import globalVal as gv

#-----------------------------------------------------------------------------
# Init the dummy nodes information list for testing.

# Dummu node data formate: 
# 'no':         Node id (int)
# 'name':       Node Name (str)
# 'ipAddr':     Node IP address(str)
# 'lat':        Node GPS latitude (float) 
# 'lng':        Node GOS longitude(float)
# 'type':       Node Type(str: "HB"-Hub, "GW"-Gateway) 
# 'rptTo':      Report to Node ID (int)
# 'comTo':      Communication node ID list( [int ...] )
# 'actF':       Activation flag (Boolean)

#--------------------------------------------------------------------------------------------------------

def parseNodes(info):
    """ Parse input database data 

    Args:
        info ([type]): [description]

    Returns:
        [type]: [description]
    """
    result = []
        
    for nodes in info:
        currNode = {}
        currList = list(nodes)
        connection = []

        currNode['no'] = currList[0]
        currNode['name'] = currList[1]
        currNode['ipAddr'] = currList[2]
        currNode['lat'] = currList[3]
        currNode['lng'] = currList[4]
        currNode['actF'] = currList[5]
        currNode['rptTo'] = currList[6]
        currNode['type'] = currList[7]

        for i in info:
            appendList = list(i)
            if currList[7] == 'HB':
                connection.append(currList[0])
                break
            if appendList[7] == 'GW' and appendList[0] != currList[0]: 
                connection.append(appendList[0])

        currNode['comTo'] = connection

        result.append(currNode)
    return result

connection = sqlite3.connect('node_database.db')
node_cursor = connection.cursor() # Cursor can be used to call execute method for SQL queries

node_cursor.execute("SELECT * FROM gatewayInfo")
db_data = node_cursor.fetchall()

DUMMY_NODES = parseNodes(db_data)

#--------------------------------------------------------------------------------------------------------
# Initialize the Flask application
app = Flask(__name__)

@app.route('/nodes', methods=['GET'])
def home():
    """ Handle the node init request."""
    return jsonify(DUMMY_NODES)

@app.route('/updates', methods=['GET'])
def updateNodeAct():
    """ Handle the node state update request.d"""
    update_connection = sqlite3.connect('node_database.db') # Reconnect due to new thread
    update_cursor = update_connection.cursor()
    update_cursor.execute("SELECT * FROM gatewayState WHERE time > {}".format(gv.gLatestTime))
    update_json_list = update_cursor.fetchall()
    if len(update_json_list) > 0: gv.gLatestTime = update_json_list[-1][0]

    changeList = [] # e.g. [{'no': [1], 'updateInfo': {'id1': {'comTo': [], 'throughputIn': 0, 'throughputOut': 0, 'actF': 0}}}]

    for data in update_json_list:
        curr_data_info = {str(data[1]):json.loads(data[2])}
        changeList.append(curr_data_info)
   
    return jsonify(changeList)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, threaded=True)