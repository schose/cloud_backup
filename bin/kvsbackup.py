import sys, os, socket
import splunk 
import logging, logging.handlers
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import urllib 
import json
import re
import random
import time
import xml.dom.minidom, xml.sax.saxutils
import basefunctions
import argparse
from time import sleep
from builtins import str


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.modularinput import *
# import splunklib.client as client

    
def usage():
    print("usage: %s [--scheme|--validate-arguments]")
    sys.exit(2)

class kvstorebackup(Script):

    def get_validation_data():

        logging.debug("in get_validation_data function")
        val_data = {}

        # read everything from stdin
        val_str = sys.stdin.read()

        # parse the validation XML
        doc = xml.dom.minidom.parseString(val_str)
        root = doc.documentElement

        #logging.debug("XML: found items")

        sessionkey_node = root.getElementsByTagName("session_key")[0]
        sessionkey = sessionkey_node.firstChild.data

        server_uri = root.getElementsByTagName("server_uri")[0]
        server_uri = server_uri.firstChild.data

        item_node = root.getElementsByTagName("configuration")[0]
        if item_node:
            logging.debug("XML: found configuration")

            name = item_node.getAttribute("name")
            val_data["stanza"] = name

            params_node = item_node.getElementsByTagName("param")
            for param in params_node:
                name = param.getAttribute("name")
                logging.debug("Found param %s" % name)
                if name and param.firstChild and \
                                param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                    val_data[name] = param.firstChild.data
        
        logging.debug("out get_validation_data function")

        val_data['session_key'] = sessionkey
        val_data['server_uri'] = server_uri
        
        return val_data
        

    def get_scheme(self):
        # # Returns scheme.
        # scheme = Scheme("BuBa modular input")
        # scheme.description = "this is a test description"
        # scheme.use_external_validation = False
        # scheme.use_single_instance = True
        
        # configfile = Argument("configfile")
        # configfile.title = "BuBa role"
        # configfile.data_type = Argument.data_type_string
        # configfile.description = "configfile for buba"
        # configfile.required_on_create = True
        # configfile.required_on_edit = True
        # scheme.add_argument(configfile)

        scheme = """<scheme>
            <title>kvstorebackup</title>
            <description>kvstore backup implementation</description>
            <use_external_validation>true</use_external_validation>
            <use_single_instance>true</use_single_instance>
            <endpoint>
                <args>
                    <arg name="env">
                        <title>enviroment</title>
                        <description>enviroment config is for</description>
                    </arg>
                </args>
            </endpoint>
        </scheme>
        """

        print(scheme)
        #return scheme
 
    def validate_input(self, validation_definition):
        # Validates input.
        pass

    def config_read(configfile, env): 

        # outputs
            # "url":"https: //localhost:8089",
            # "idx_meta":"bubameta",
            # "token":"eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIGFuZHJlYXNzLU1hY0Jvb2stUHJvLmxvY2FsIiwic3ViIjoiYWRtaW4iLCJhdWQiOiJ0ZXN0IiwiaWRwIjoiU3BsdW5rIiwianRpIjoiNzRhNjA4Yzg5N2VlZjI1MzAwYTg2NWJkZmQ4MDdmY2FjY2Q5NTNkZmE2ZmYxM2U2NmZkMDk4ZjY0NWM3OGQ5NCIsImlhdCI6MTYyMzA3NTM2MiwiZXhwIjoxNjQ4OTk1MzYyLCJuYnIiOjE2MjMwNzUzNjJ9._AOnFCn50FV_EDLoiqyvTlDnbL4jlELyD-4w87tEy2tSmq7LaHmdk4RMUH1rIt_LAqT_GXMVuDB_8pjR_9ApYg",
            # "idxurl":"https://127.0.0.1:8089",
            # "idxusername":"admin",
            # "idxpassword":"Password01",
            # "archive":"",


        import configparser
        config = configparser.ConfigParser()
        config.read(configfile)

        out = {}
        #print(config['env'])

        for key in config[env].keys():
            out[key] = config[env][key]

        out['environment'] = env

        return out

    # def get_session_key(username, password):

    #     splunkurl = 'https://localhost:8089/services/auth/login'

    #     parameters = {  "username": username,
    #                 "password": password,
    #                 "output_mode": "json" }

    #     r = requests.post(splunkurl, data=urllib.parse.urlencode(parameters), verify=False)
    #     response = json.loads(r.text)
    #     logging.debug("sessionkey: " + response['sessionKey'])

    #     return response['sessionKey']


    def stream_events(self):
        # Splunk Enterprise calls the modular input, 
        # streams XML describing the inputs to stdin,
        # and waits for XML on stdout describing events.

        logging.debug("in stream_events")

        # # debug me in vs code
        # import sys, os
        # sys.path.append(os.path.join(os.environ['SPLUNK_HOME'],'etc','apps','SA-VSCode','bin'))
        # import splunk_debug as dbg
        # dbg.enable_debugging(timeout=25)

        parser = argparse.ArgumentParser()
        parser.add_argument('--env', help='set env', default="singlerestore")
        parser.add_argument('--debug', help='just for debugging')

        args = parser.parse_args()

        # # when started with --debug flag - from commandline ( for debugging ).. otherwise read the input from splunk
        # if len(args.debug)>0:
        #     logging.debug("i was started from commandline")
        #     env = "singlerestore"
        #     # session key from commandline
        #     # this is for test env
        #     tmp_username = 'admin'
        #     tmp_password = 'Password01'
        #     tmp_sessionkey = kvstorebackup.get_session_key(tmp_username, tmp_password)
        #     tmp_serveruri = 'https://127.0.0.1:8089'
        #     logging.debug("using new sessionkey as you are using --debug: " + tmp_sessionkey)
        # else:
        # get data from input
        val_data = kvstorebackup.get_validation_data()
        logging.debug("got parameter env = " + str(val_data['env']))
        env = val_data['env']
        tmp_sessionkey = val_data['session_key']
        tmp_serveruri = val_data['server_uri']

        logging.debug("now run code in stream functions..")

        stream = os.popen(str(env))
        output = stream.read()
        
        logging.debug("output: " + output)

if __name__ == "__main__":

    logging = basefunctions.setup_logging()
    #sessionkey = get_session_key()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug=true":
            kvstorebackup().stream_events()
        elif sys.argv[1] == "--scheme": 
            kvstorebackup().get_scheme()
        elif sys.argv[1] == "--validate-arguments":
            kvstorebackup().stream_events()
        else: 
            usage()

    else:
        kvstorebackup().stream_events()

    #sys.exit(kvstorebackup().run(sys.argv))