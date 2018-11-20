from flask import Flask, url_for
import os
from kubernetes import client, config
from pprint import pprint

app = Flask(__name__)


def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]


def get_florida_string():
    config.load_incluster_config()

    v1 = client.CoreV1Api()

    #this probably todo needs an environment variable for the pod selector
    podlist = v1.list_namespaced_pod("default", label_selector='app=dynomite,role=worker')

    floridastring = ""
    for item in podlist.items:
        podip = item.status.pod_ip
        generatename = item.metadata.generate_name
        name = item.metadata.name
        token = item.spec.containers[0].env[0].value
        token = token.replace("'", "")
        name = name.replace(generatename, "")
        rackname = "us-east-" + name
        #most likely todo need a namespace for rack and search for labelled port?
        florida = podip.strip() + ":8101:" + rackname.strip() + ":dc1:" + token.strip()
        floridastring = floridastring + florida + "|"

    floridastring = rreplace(floridastring, "|", "", 1)
    return floridastring


@app.route('/REST/v1/admin/get_seeds')
def florida():
    return get_florida_string()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('PRODUCTION') is None
    app.run(debug=debug, host='0.0.0.0', port=port)
