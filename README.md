

# Gateway-Topographic-Map

```
 All copyrights reserved by NUS-Singtel Cyber Security R&D Lab (Jun 2016 to Jun 2021)
```

**Program Design Purpose**: We want to create  web host program with database to provide a topographic map panel website to show gateway devices' information (geo-location, communication details, detail current working state). 

[TOC]

### Introduction

This project will create a map panel to show gateway devices' communication situation topographic. It is is a sub-project of the ‘QSG-Manager dashboard’ (Quantum Safe Gateway Manager) project. In the main ‘Quantum Safe Gateway’ project, there will be several gateway devices communicating with each other. QSG-Manager will collect and monitor the internal status of our gateway devices and visualize all the data. 

Assume we have two gateway devices (gateway A and B) deployed in NTU and NUS. When these two gateways are communicating with each other, on the topographic map panel we will mark these two gateway GPS position on the map and draw a link between the 2 markers:

![](doc/img/rm_preview.png)

###### Gateway-Topographic-Map Main Page View

Users are able to interact with the map by clicking on a marker for a popup showing the full details of gateway throughput and data rate between the 2 gateways.

There is also a sidebar attached beside the map which allow users to decide various map settings. They can choose the data update rate of the flask webserver calling GET request through a dropdown menu. A filter function is also added to only display certain types of communication links (active, gateway, control hub).

![](doc/img/map.gif)

###### The main workflow for the program

![](doc/img/workflow.png)

Version V_0.2

------

### Program Setup

###### Development Environment 

Python3.7.4, HTML+flask, socketIO+eventlet, SQLite3

###### Additional Lib/Software Need

1. **python Flask** : https://www.fullstackpython.com/flask.html

   ```
   Installation cmd: pip3 install Flask
   ```

3. **flask-socketIO 4.5.1**: https://flask-socketio.readthedocs.io/en/latest/

   ```
   Installation cmd: pip3 install flask-socketio
   ```

4. **SQL Browser**: https://sqlitebrowser.org/blog/version-3-12-2-released/

4. **python eventlet**: https://pypi.org/project/eventlet/

   ```
   pip3 install eventlet
   ```

5. --

###### Hardware Needed : None

###### Program Files List 

version: v0.2

| Program File             | Execution Env | Description                                                  |
| ------------------------ | ------------- | ------------------------------------------------------------ |
| src/topologyMapHost.py   | python3       | This module is used create flask webserver to send GET request with the QSG-Manager. |
| src/globalVal.py         | python3       | This module stores all the global variables used in the flask webserver. |
| src/node_database.db     |               | Database file.                                               |
| src/databaseCreater.py   |               | Module to insert the simulation data into the data base.     |
| src/Log.py               |               | Log generation mode.                                         |
| src/NodesRcd.txt         |               | File to save simulation node information.                    |
| src/ConfigLoader.py      | python3       | Module to load the node record file.                         |
| src/templates/index.html | HTML          | This file generates the UI of the Topological Maps using Google Maps. |
| src/static/js/maps.js    | JavaScript    | This module stores the static JS functions to run the Google Map. |
| src/static/css/map.css   | CSS           | This is the stylesheet for the Topological Map.              |
| src/static/img           |               | Image file used by the web page.                             |



------

### Program Usage

###### Program Execution Cmd 

1. Start up the data insert simulation program to add new gateway 
   ```
   python3 databaseCreater.py
   ```

   Module API Usage: call `updateStateTable(self, gatewayID, infoStr)` to insert the new gateway state in to database.
   
2. Run the flask webserver to retrieve data from the QSG-Manager

   ```
   python3 topologyMapHost.py
   ```

   **After running step2, wait 30 sec make sure the database thread fully started then do step 3.**

3. Open web browser and enter URL: http://127.0.0.1:5000



###### Web Page Usage

![](doc/img/UI_view.png)



------

### Problem and Solution

###### Problem[0] **:** Unable to run flask server and socketIO concurrently due to threading issues

**OS Platform** : Windows

**Error Message**: greenlet.error: cannot switch to a different thread

**Type**: Setup exception

**Solution**:

Upgrade Python 2.7 to Python 3.x to run Eventlet successfully. Alternatively, use gevent and gevent-socket library instead of eventlet:

- Step 1: Uninstall eventlet library: pip3 uninstall eventlet
- Step 2: Install gevent: pip3 install gevent
- Step 3: Install gevent-socket: pip3 install gevent-socket



------

### Reference Link

- N.A

  

------

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 08/12/2021