#-----------------------------------------------------------------------------
# Name:        webGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2020/11/24
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

"""
For good coding practice, follow the following naming convention:
    1) Global variables should be defined with initial character 'g'
    2) Global instances should be defined with initial character 'i'
    2) Global CONSTANTS should be defined with UPPER_CASE letters
"""

import os
print("Current working directory is : %s" % os.getcwd())
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)
APP_NAME = 'topologyMapHost_v0.1'

#------<CONSTANTS>-------------------------------------------------------------

DB_PATH = os.path.join(dirpath , 'node_database.db')
NODES_FILE = os.path.join(dirpath, 'NodesRcd.txt')

# Google map API billing key:
MAP_API_KEY = 'AIzaSyBoHBPqxFw40DFvCbXrj1IWNcvkzb6WkkI' # replace this with your own key.

# Gateway marker link
GW_MK_LK = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
# Gateway information box icon link
GW_IB_LK = '../static/images/gateway.jpg'
# Control hub marker lnik
HB_MK_LK = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
# Control hub information box img link
HB_IB_LK = '../static/images/hub.jpg'

CH_GPS = (1.2988469, 103.8360123) # control hub gps location currently we use Singtel Comcenter POS.

#-------<GLOBAL VARIABLES (start with "g")>------------------------------------
# VARIABLES are the built in data type.
gPeriod = 10
gMapFilter = ['show-inactive', 'show-gateway', 'show-control']
gMapSetting = [1, 1, 1] # Inactive, gateway, control hub communications respectively
gDevNode = []   
gLatestTime = 0.0

#-------<GLOBAL INSTANCES (start with "i")>-----------------------------------------------------
# INSTANCES are the object. 
iDataMgr = None
iSocketIO = None