# Module which creates a database for testing

import json
import random
import sqlite3
import time

from sqlite3 import Error

sql_gatewayInfo_table = "CREATE TABLE IF NOT EXISTS gatewayInfo(id integer PRIMARY KEY, name text NOT NULL, ipAddr text NOT NULL, lat float NOT NULL, lng float NOT NULL, actF integer NOT NULL, rptTo integer NOT NULL, type text NOT NULL)"
sql_gatewayState_table = "CREATE TABLE IF NOT EXISTS gatewayState(time float PRIMARY KEY, id text NOT NULL, updateInfo text NOT NULL)"

# Choose 2 connection to toggle
DUMMY_TIME = 19.01 # Start the initial time as 19.01
DUMMY_ID_LIST = [] # Updates the ID list
DUMMY_JSON_INFO = {}

DUMMY_NODES = [
    {'no': 0,
        'name':     "Control Hub",
        'ipAddr':   "10.0.0.0",
        'lat':      1.2988469,
        'lng':      103.8360123,
        'type':     'HB', 
        'rptTo':    0,
        'actF':     0},

    {'no': 1,
        'name':     "NUS",
        'ipAddr':   "10.0.0.1",
        'lat':      1.2964053,
        'lng':      103.7690442,
        'type':     'GW',
        'rptTo':    0,
        'actF':     0},

    {'no': 2,
        'name':     "NTU",
        'ipAddr':   "10.0.0.2",
        'lat':      1.3461474,
        'lng':      103.6793512,
        'type':     'GW',
        'rptTo':    0,
        'actF':     0},

    {'no': 3,
        'name':     "SUTD",
        'ipAddr':   "10.0.0.3",
        'lat':      1.3413,
        'lng':      103.9638,
        'type':     'GW', 
        'rptTo':    0,
        'actF':     0},

    {'no': 4,
        'name':     "SMU",
        'ipAddr':   "10.0.0.4",
        'lat':      1.296568,
        'lng':      103.852119,
        'type':     'GW',
        'rptTo':    5,
        'actF':     0},

    {'no': 5,
        'name':     "Control Hub",
        'ipAddr':   "10.0.0.5",
        'lat':      1.3525,
        'lng':      103.9447,
        'type':     'HB',
        'rptTo':    5,
        'actF':     0}
]

#====================================================================================================

def sql_connection():
    try:
        # Create a connection with the database
        connection = sqlite3.connect('node_database.db')
        print("Connection is established: Database is created in node_database.db")
        return connection
    except Error:
        print(Error)

def sql_create_table():
    try:
        cursorObj.execute(sql_gatewayInfo_table)
        connection.commit()
        cursorObj.execute(sql_gatewayState_table)
        connection.commit()
        for node in DUMMY_NODES:
            insert_statement = 'INSERT INTO gatewayInfo VALUES({}, "{}", "{}", {}, {}, {}, {}, "{}")'.format(node["no"], node["name"], node["ipAddr"], node["lat"], node["lng"], node["actF"], node["rptTo"], node["type"])
            cursorObj.execute(insert_statement)
            connection.commit()
    except Error: print(Error)

def sql_clear_table():
    cursorObj.execute('DELETE FROM gatewayState')
    connection.commit()

def update_id_list(num):
    DUMMY_ID_LIST.clear()
    DUMMY_ID_LIST.append(num)

def update_json_info(id):
    DUMMY_JSON_INFO.clear()
    id_information = {}
    actF_status = random.getrandbits(1)
    comTo_list = [i for i in range(5)] # Create a list with all the nodes
    if id == 0 or id == 4:
        comTo_list.remove(0)
        comTo_list.remove(4)
    else: comTo_list.remove(id)
    comTo_list = random.sample(comTo_list, k=random.randrange(3))

    # Fill up the id information for that node
    id_information['comTo'] = comTo_list
    id_information['throughputIn'] = round(random.uniform(1, 10), 2) if actF_status else 0
    id_information['throughputOut'] = round(random.uniform(1, 10), 2) if actF_status else 0
    id_information['actF'] = actF_status

    DUMMY_JSON_INFO['id{}'.format(id)] = id_information
    return json.dumps(DUMMY_JSON_INFO)

def sql_close(connection):
    print("Closing database connection")
    connection.close()

#====================================================================================================

connection = sql_connection()
cursorObj = connection.cursor() # Cursor can be used to call execute method for SQL queries
sql_clear_table() # Clear the previous test case

# sql_create_table() # When there is a need to recreate the table

# Test case: To sleep for a period and update at every 3 seconds interval
while True:
    # Increase the time. Toggle the id and updateInfo
    DUMMY_TIME += 0.03
    rand_node = random.randrange(5)
    update_id_list(rand_node)
    json_info_string = update_json_info(rand_node)

    # Create the insert statement to change the database
    insert_statement = "INSERT INTO gatewayState(time, id, updateInfo) VALUES({}, '{}', '{}')".format(DUMMY_TIME, str(DUMMY_ID_LIST), json_info_string)
    cursorObj.execute(insert_statement)
    connection.commit()
    time.sleep(3)

sql_close(connection)