from flask import Flask, url_for
import os
from kubernetes import client, config
from pprint import pprint

app = Flask(__name__)


def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]


def get_florida_string():
    # security token hardcoded for now.... todo I'll have to make this an environment variable later
    aToken = <your kubernetes token here>

    # Create a configuration object
    aConfiguration = client.Configuration()

    # endpoint for kubes api... todo make this an environment variable again
    aConfiguration.host = <your kubernetes api host here>

    # Security part.

    aConfiguration.verify_ssl = False
    # if you want to do it you can with these 2 parameters this is probably a todo but I'm not doing it now, sorry :)
    # configuration.verify_ssl=True
    # ssl_ca_cert is the filepath to the file that contains the certificate.
    # configuration.ssl_ca_cert="certificate"

    aConfiguration.api_key = {"authorization": "Bearer " + aToken}

    # Create a ApiClient with our config
    aApiClient = client.ApiClient(aConfiguration)

    # Do calls
    v1 = client.CoreV1Api(aApiClient)

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
        rackname = "RACK" + name
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
