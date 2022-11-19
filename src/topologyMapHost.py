#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        topologyMapHost.py [python3]
#
# Purpose:     This module will create a topographic map to show deployed gateway 
#              devices communication situation. It is is a sub-project of the 
#              'QSG-Manager dashboard' (Quantum Safe Gateway Manager) project. 
#              
# Author:      Liu Yuancheng
#
# version:     v_0.2
# Created:     2020/05/22
# Copyright:   Singtel Cyber Security Research & Development Laboratory
# License:     
#-----------------------------------------------------------------------------

# import python built in modules.
import os
import time
import json
import sqlite3
import threading
from copy import deepcopy

# import pip installed modules.
from flask import Flask, render_template, request
# Install flask socketio library: pip3 install flask_socketio
from flask_socketio import SocketIO

# import project local modules.
import Log
import globalVal as gv

# Set this module execution flags.
TEST_MODE = True    # Test mode flag - True: test on local computer.
LOG_FLAG = True     # log information display flag.
HOST_IP = '127.0.0.1' if TEST_MODE else '0.0.0.0'
HOST_PORT = 5000
NODE_INFO_QUERY = "SELECT * FROM gatewayInfo"

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['DEBUG'] = True  
gv.iSocketIO = SocketIO(app)

#----------------------------------------------------------------------------------------------------
# Server setup function
@app.route('/', methods=['GET', 'POST'])
def home():
    Log.info("flask app: route request.", printFlag=LOG_FLAG)
    if request.method == 'POST':
        gv.gPeriod = int(request.form['rate-uptake'])
        for idx, data in enumerate(gv.gMapFilter):
            gv.gMapSetting[idx] = 1 if request.form.get(data) != None else 0
        if gv.iDataMgr: gv.iDataMgr.setUpdateRate(gv.gPeriod)
    return render_template("index.html", 
                            gateway=gv.iDataMgr.getMarkersJSON(), 
                            period=gv.gPeriod, 
                            setting=gv.gMapSetting)

@gv.iSocketIO.on('connect', namespace='/test')
def test_connect():
    Log.info("SocketIO: Client connected.", printFlag=LOG_FLAG)

@gv.iSocketIO.on('disconnect', namespace='/test')
def test_disconnect():
    Log.info("SocketIO: Client disconnected.", printFlag=LOG_FLAG)

#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class DevNode(object):
    """ Create the device node object. This class was under editing."""
    def __init__(self, devID=None, devName=None, devType=None, devGPS=None):
        # parameter should be set during init.
        self.devID = devID
        self.devName = devName
        self.devType = devType
        self.devGPS = devGPS
        # parameters with the default values
        self.ipAddr = "127.0.0.1"   # gateway public IP address.
        self.comNodeIDs = []        # gateway ID list this node is communicating with.
        self.keyExchange = []        # gateway ID list this node conducted key exchange with.
        self.rptNodeID = 0          # the hub ID node need to report. None if the node is a hub.     
        self.activeFlag = True      # node activate flag
        self.inThrput = 0           # incoming data through put (Mbps/s)
        self.outThrput = 0          # out going data through put (Mbps/s)
        self.encryptEnable = False  # encryption enable flag.

#----------------------------------------------------------------------------------------------------
    def getNodeID(self):
        return  self.devID

#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class DataMgr(threading.Thread):
    """ Map data manager thread running parallel with the main flask web host thread to load data 
        from data base periodically and generate node makers, com links ..."""
    def __init__(self, parent, threadID, name):
        threading.Thread.__init__(self)
        self.parent = parent
        self.hubID = []     # report hub ID list 
        self.nodeDict = {}  # all nodes dict.
        self.periodic = 10  # default update every 10 sec
        self.linkDict = {'no':None, 'pts':None, 'active':None, 'keyExchange': None, 'throughput1':None, 'throughput2': None} 
        # example: {'no':1, 'pts':'0-1', 'active':True, 'keyExchange': True, 'throughput1':10.21, 'throughput2': 5.52}
        self.linkList = []  # link list, each element should be a linkDict.
        # Init the data base manager
        try:
            self.dbMgr = sqlite3.connect(gv.DB_PATH, check_same_thread=False)
            self.nodeCursor = self.dbMgr.cursor() # Cursor can be used to call execute method for SQL queries
        except sqlite3.Error as Error:
            print("__init__ error: %s" %str(Error))
            exit()
        self.terminate = False
        Log.info("DataMgr: Data manager thread inited.", printFlag=LOG_FLAG)

#------------------------------------------------------------------------------------
    def _buildComLink(self):
        """ build the communication link list based on the node's <DevNode.comNodeIDs>."""
        for node in self.nodeDict.values():
            if node.devID in self.hubID: continue # jump over the control hub.
            # build the gateway->hub report link:
            rptlink = deepcopy(self.linkDict)
            rptlink['no'] = len(self.linkList)
            rptlink['pts'] = '-'.join((str(node.rptNodeID), str(node.devID)))
            rptlink['active'] = node.activeFlag
            if not self._checkLinkExist(rptlink['pts']): self.linkList.append(rptlink)
            # build the gateway<->gateway communication links:
            for pairID in node.comNodeIDs:
                comlink = deepcopy(self.linkDict)
                comlink['no'] = len(self.linkList)
                pair = [node.devID, pairID]
                pair.sort() # make sure the pts format follow 'pts': <smaller_id>-<bigger_id> 
                comlink['pts'] = '-'.join([str(i) for i in pair])
                comlink['active'] = node.activeFlag
                if not self._checkLinkExist(comlink['pts']): self.linkList.append(comlink)
        
        # print all the build link
        _ = [Log.info("DataMgr: created link: %s", str(link), printFlag=LOG_FLAG) for link in self.linkList]

#----------------------------------------------------------------------------------------------------
    def loadNodesData(self):
        """ Load gateways and control hub google map markers data from the database."""
        # node data example : [5,Control Hub 2, 10.0.0.5, 1.3525, 103.9447, 0, 5, HB]
        self.nodeCursor.execute(NODE_INFO_QUERY)
        data = self.nodeCursor.fetchall()
        Log.info("DataMgr : all nodes information: %s", str(data), printFlag=LOG_FLAG)
        gwIDlist = [i[0] for i in data] 
        for nodeData in data:
            currList = list(nodeData)
            nodeID = currList[0]
            node = DevNode(devID=nodeID,
                           devName=currList[1],
                           devType=currList[7],
                           devGPS=(currList[3], currList[4]))
            # Set the node parameters:
            node.ipAddr = currList[2]
            node.comNodeIDs = []
            if currList[7] == 'HB': 
                self.hubID.append(nodeID)
                node.comNodeIDs = [nodeID]  
            elif currList[7] == 'GW':
                node.comNodeIDs = deepcopy(gwIDlist)
                node.comNodeIDs.remove(nodeID)
            node.rptNodeID = currList[6]
            node.activeFlag = currList[5]
            # Append the node it node dict.
            self.nodeDict[str(nodeID)] = node
        # Buid the communication link based on the node com-pair relationship.
        self._buildComLink()

#------------------------------------------------------------------------------------          
    def _checkLinkExist(self, ptsStr):
        """ Check whether a link is exist. Input: a link pts str (example: '1-2')"""
        for link in self.linkList:
            if link['pts'] == ptsStr: return True
        return False

#------------------------------------------------------------------------------------
    def getCommJSON(self):
        """ Convert the communication link data list to Json string which will
            be used by the Map front end javascript.
        """
        result = {}
        for idx, data in enumerate(self.linkList):
            result[idx] = {
                'connection': data['pts'],
                'active': data['active'],
                'keyExchange': data['keyExchange'], 
                'throughput1': data['throughput1'], 
                'throughput2': data['throughput2']
            }
        return json.dumps(result)

#-----------------------------------------------------------------------------------
    def getMarkersJSON(self):
        """ Get the Nodes' markers JSON string which will be used by the Map front
            end javascript.
        """
        result = {}
        # Filter the data to get name and coordinates
        for node in self.nodeDict.values():
            header = "" if "Hub" in node.devName else "Gateway[%s] " % str(
                node.devID)
            result[node.devID] = {
                'name': header + node.devName,
                'number': node.devID,
                'pos': {'lat': node.devGPS[0], 'lng': node.devGPS[1]}
            }
        return json.dumps(result)

#------------------------------------------------------------------------------------
    def getNodeActJSON(self):
        """ Get the nNode activation situation JSON string which will be used by the 
            Map front end java script.
        """
        result = {}
        for nodePair in self.nodeDict.items():
            (idx, node) = nodePair
            result[idx] = node.activeFlag
        return json.dumps(result)

#------------------------------------------------------------------------------------
    def updateLink(self):
        """ Load the current node state and create the communication link data for 
            <SocketIO.emit()> to update the map page's link detail.
        """
        self.updateNodes()
        # Go through link list to update the link active flag base on Node activate states.
        for i in range(len(self.linkList)):
            linkAct = True  # Check whether the link is active or not
            self.linkList[i]['keyExchange'] = False # Check whether the nodes have done key exchange
            commList = self.linkList[i]['pts'].split('-') # Example: "1-2" = ["1", "2"]
            # check if node 1 in node 2's keyExchange list and node 2 in node 1's keyExchange list.
            if int(commList[0]) in self.nodeDict[str(commList[1])].keyExchange and int(commList[1]) in self.nodeDict[str(commList[0])].keyExchange:
                self.linkList[i]['keyExchange'] = True # Set key exchange to true if both node contains comTo
            #self.linkList[i]['keyExchange'] = linkKey

            for idx in [int(i) for i in commList]:
                linkAct = linkAct and self.nodeDict[str(idx)].activeFlag
            self.linkList[i]['active'] = linkAct

            # Connect the server for throughput information else give 0
            self.linkList[i]['throughput1'] = self.nodeDict[str(commList[0])].inThrput if linkAct else 0
            self.linkList[i]['throughput2'] = self.nodeDict[str(commList[1])].inThrput if linkAct else 0

        Log.info("link list: %s" %str(self.linkList))
        # Update the web page link
        gv.iSocketIO.emit('newrequest', {'comm': self.getCommJSON(),
                                         'activation_circles': self.getNodeActJSON()}, namespace='/test')

#------------------------------------------------------------------------------------
    def updateNodes(self):
        """ Connet to the QSG-manager host to load the latest Node update information."""
        self.nodeCursor.execute("SELECT * FROM gatewayState WHERE time > {}".format(gv.gLatestTime))
        data = self.nodeCursor.fetchall()
        if len(data) > 0: gv.gLatestTime = data[-1][0]
        #changeList = [] # e.g. [{'no': [1], 'updateInfo': {'id1': {'comTo': [], 'throughputIn': 0, 'throughputOut': 0, 'actF': 0}}}]
        Log.info("DataMgr: Node update data : %s", str(data), printFlag=LOG_FLAG)
        for state in data:
            key, val = str(state[1]), json.loads(state[2])
            self.nodeDict[key].keyExchange = val['comTo']
            self.nodeDict[key].inThrput = val['throughputIn']
            self.nodeDict[key].outThrput = val['throughputOut']
            self.nodeDict[key].activeFlag = val['actF']

#-----------------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        Log.info("gv.iDataMgr: run() function loop start, terminate flag [%s]", str(
            self.terminate), printFlag=LOG_FLAG)
        time.sleep(1)  # sleep 1 second to wait socketIO start to run.
        while not self.terminate:
            self.updateLink()
            gv.iSocketIO.sleep(self.periodic)

#-----------------------------------------------------------------------------------
    def setUpdateRate(self, periodic):        
        self.periodic = periodic
        Log.info("gv.iDataMgr: Set update periodic to %s", str(self.periodic), printFlag=LOG_FLAG)

#----------------------------------------------------------------------------------------------------
    def stop(self):
        """ Stop the thread."""
        self.terminate = True


#----------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
def main():
    # Init the logger: 
    TOPDIR = 'src'                      # folder name where we put Logs, Maps, etc
    gWD = os.getcwd()
    idx = gWD.find(TOPDIR)
    if idx != -1:
        gTopDir = gWD[:idx + len(TOPDIR)]
    else:
        gTopDir = gWD   # did not find TOPDIR - use WD
    print('gTopDir:%s' % gTopDir)
    Log.initLogger(gTopDir, 'Logs', gv.APP_NAME, gv.APP_NAME,
            historyCnt=100, 
            fPutLogsUnderDate=True)

    gv.iDataMgr = DataMgr(None, 0, "server thread")
    gv.iDataMgr.loadNodesData()
    gv.iDataMgr.start()
    gv.iSocketIO.run(app, host=HOST_IP, port=HOST_PORT)

#----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    print('End of __main__')
