from flask import Flask
import os
from kubernetes import client, config
import random
import requests

app = Flask(__name__)


def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]

def get_pod_list():
    
    config.load_kube_config(config_file="./config")
    
    v1 = client.CoreV1Api()
    
    namespace = os.environ.get('NAMESPACE')

    # this probably todo needs an environment variable for the pod selector
    list = v1.list_namespaced_pod(namespace, label_selector='app=dynomite,role=worker')
    return list.items

def parse_item(item):
    #this is very weird but conductor fails when you have more than 4 racks per dc?
    alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    podip = item.status.pod_ip
    generatename = item.metadata.generate_name
    fullname = item.metadata.name
    token = item.spec.containers[1].env[0].value
    token = token.replace("'", "")
    name = fullname.replace(generatename, "")
    number = int(name)
    rackname = generatename[:-1] + alpha[number]
    # most likely todo need a namespace for rack and search for labelled port?
    items = [podip, rackname, token, fullname, generatename[:-1]]
    return items

def check_dynomite():
    items = get_pod_list()
    floridastring = ""
    for item in items:
        items = parse_item(item)
        ip = items[0].strip()
        url = "http://"+ip+":22222/info"
        r = requests.get(url)
        if(r.status_code == 200) :
            return "ok"

    raise Exception('No Dynomite Nodes Resonding')


def get_florida_string():
    items = get_pod_list()
    floridastring = ""
    for item in items:
        items = parse_item(item)
        florida = items[0].strip() + ":8101:" + items[1].strip() + ":"+ items[4].strip() +":" + items[2].strip()
        floridastring = floridastring + florida + "|"

    floridastring = rreplace(floridastring, "|", "", 1)
    return floridastring

def get_conductor_string():
    items = get_pod_list()
    conductorstring = ""
    filestring = ""

    random.shuffle(items)

   
    for item in items:
        items = parse_item(item)
        # most likely todo need a namespace for rack and search for labelled port?
        conductor = items[3].strip() + ":8102:" + items[1].strip()
        #host1:8102:us-east-1c;
        conductorstring = conductorstring + conductor + ";"
        

    conductorstring = rreplace(conductorstring, ";", "", 1)

    with open('config.properties', 'r') as myfile:
        filestring = myfile.read().replace('REPLACEME', conductorstring)

    return filestring


@app.route('/REST/v1/admin/get_seeds')
def florida():
    return get_florida_string()


@app.route('/REST/v1/admin/config.properties')
def conductor():
    return get_conductor_string()

@app.route('/REST/v1/admin/check_dynomite')
def dynomite():
    return check_dynomite()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('PRODUCTION') is None
    app.run(debug=debug, host='0.0.0.0', port=port)
