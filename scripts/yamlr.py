#!/usr/bin/python
import json, requests, jsonify, datetime, os, yaml, re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def f5Connect(appliance, username, password, uri, method):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json' }
    if method == "GET":
        response = requests.get('https://' + appliance + uri, auth=(username, password),headers=headers, verify=False)
    return response

def nodeYamlr(nodeName, partition, appliance, username, password):
    response = f5Connect(appliance, username, password, '/mgmt/tm/ltm/node/~'+ partition +'~'+ nodeName, "GET" )
    if "errorStack" in response.json():
        raise Exception(response.json()['message'])
    else:
        # Define the var filename
        fileName = response.json()["name"].replace(".", "_") + ".yml"
        nodeYaml = { response.json()["name"].replace(".", "_") : response.json() }
        # Create host_var file
        if not os.path.exists("../f5_vars/nodes"):
            os.makedirs("../f5_vars/nodes")
        newFile = open("../f5_vars/nodes/" + fileName, "wb")
        newFile.write(yaml.safe_dump(nodeYaml,indent=4, allow_unicode=True, default_flow_style=False));
        newFile.close()
        print fileName + " created"

        return response

def poolYamlr(poolName, partition, appliance, username, password):
    response = f5Connect(appliance, username, password, '/mgmt/tm/ltm/pool/~'+ partition +'~'+ poolName, "GET" )
    poolMembers = f5Connect(appliance, username, password, '/mgmt/tm/ltm/pool/~'+ partition +'~'+ poolName+'/members', "GET" )

    if "errorStack" in response.json():
        raise Exception(response.json()['message'])
    else:
        # split name into host and port, when adding nodes you cant add in that same format
        x = 0
        poolMembersJson = poolMembers.json()["items"]
        for poolMember in poolMembersJson:
            poolMemberName = poolMember["name"].split(":")
            poolMembersJson[x]["name"] = poolMemberName[0]
            poolMembersJson[x]["port"] = poolMemberName[1]
            nodeYamlr(poolMembersJson[x]["name"], partition, appliance, username, password)
            x = x + 1
        # combine pool members with the pool json
        responseJson = response.json()
        responseJson["poolMembers"] = poolMembersJson
        fileName = responseJson["name"].replace(".", "_") + ".yml"
        poolYaml = { responseJson["name"].replace(".", "_") : responseJson }
        if not os.path.exists("../f5_vars/pools"):
            os.makedirs("../f5_vars/pools")
        #print json.dumps(responseJson,indent=4)
        newFile = open("../f5_vars/pools/" + fileName, "wb")
        newFile.write(yaml.safe_dump(poolYaml,default_flow_style=False));
        newFile.close()
        print fileName + " created"

        if "monitor" in responseJson:
            monitors = responseJson['monitor'].split('and')

            # get all monitors so that i can determine the type of monitor it is
            monitorLibrary = f5Connect(appliance, username, password, '/mgmt/tm/ltm/monitor/', "GET" )
            monitorLibrary = monitorLibrary.json()['items']
            monitorPaths = []
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json' }
            for monitorPath in monitorLibrary:
                path = monitorPath['reference']['link'].replace("localhost", appliance)
                pathResponse = requests.get(path, auth=(username, password),headers=headers, verify=False)
                if "items" in pathResponse.json():
                    pathResponse = pathResponse.json()['items']
                    for ppath in pathResponse:
                        kind = ppath['kind'].split(':')
                        monitorPaths.append({ "name": ppath['name'], "partition": ppath['partition'], "kind": kind[3], "content": ppath})

            for monitor in monitors:
                monitorer = monitor.split("/")
                monitorPartition = monitorer[1].strip()
                monitorName = monitorer[2].strip()

                #print monitorPaths
                for searchMonitor in monitorPaths:
                    if searchMonitor['name'] == monitorName and searchMonitor['partition'] == monitorPartition:
                        searchMonitor['content']['type'] = searchMonitor['kind']
                        monitorJson = searchMonitor['content']
                        if not os.path.exists("../f5_vars/monitors/"):
                            os.makedirs("../f5_vars/monitors/")
                        if not "recv" in monitorJson:
                            monitorJson["recv"] = None
                        fileName = monitorName.replace(".", "_") + ".yml"
                        monitorYaml = { monitorJson["name"].replace(".", "_") : monitorJson }
                        newFile = open("../f5_vars/monitors/" + fileName, "wb")
                        newFile.write(yaml.safe_dump(monitorYaml,default_flow_style=False));
                        newFile.close()
                        print fileName + " created"

        return response

def iruleYamlr(iruleName, partition, appliance, username, password):
    iruleResponse = f5Connect(appliance, username, password, '/mgmt/tm/ltm/rule/~'+ partition +'~'+ iruleName +'/', "GET" )
    iruleResponse = iruleResponse.json()

    if not os.path.exists("../f5_vars/irules"):
        os.makedirs("../f5_vars/irules")
    fileName = iruleName.replace(".", "_") + ".yml"
    iruleYaml = { iruleResponse["name"].replace(".", "_") : iruleResponse }
    newFile = open("../f5_vars/irules/" + fileName, "wb")
    newFile.write(yaml.safe_dump(iruleYaml,default_flow_style=False));
    newFile.close()
    print fileName + " created"

    return iruleResponse

def datagroupYamlr(name, partition, appliance, username, password):
    dgResponse = f5Connect(appliance, username, password, '/mgmt/tm/ltm/data-group/internal/~'+ partition +'~'+ name +'/', "GET" )
    dgResponse = dgResponse.json()

    if not os.path.exists("../f5_vars/datagroups"):
        os.makedirs("../f5_vars/datagroups")
    fileName = name.replace(".", "_") + ".yml"
    dgYaml = { dgResponse["name"].replace(".", "_") : dgResponse }
    newFile = open("../f5_vars/datagroups/" + fileName, "wb")
    newFile.write(yaml.safe_dump(dgYaml,default_flow_style=False));
    newFile.close()
    print fileName + " created"

    return dgResponse


def virtualYamlr(vipName, partition, appliance, username, password):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json' }
    vipResponse = f5Connect(appliance, username, password, '/mgmt/tm/ltm/virtual/~'+ partition +'~'+ vipName, "GET" )
    vipProfiles = f5Connect(appliance, username, password, '/mgmt/tm/ltm/virtual/~'+ partition +'~'+ vipName +'/profiles', "GET" )
    vipResponseJson = vipResponse.json()
    profilesJson = vipProfiles.json()["items"]
    profiles = []
    for profile in profilesJson:
        profiles.append({ "name": "/"+ profile['partition'] + "/" + profile['name'], "context": profile['context']})
    vipResponseJson["profiles"] = profiles
    port = vipResponseJson["destination"].split(":")
    vipResponseJson["port"] = int(port[1])
    if not "pool" in vipResponseJson:
        vipResponseJson["pool"] = None
    fileName = vipResponseJson["name"].replace(".", "_") + ".yml"
    virtualYaml = { vipResponseJson["name"].replace(".", "_") : vipResponseJson }
    if not os.path.exists("../f5_vars/virtuals"):
        os.makedirs("../f5_vars/virtuals")
    #print json.dumps(vipResponseJson,indent=4)
    newFile = open("../f5_vars/virtuals/" + fileName, "wb")
    newFile.write(yaml.safe_dump(virtualYaml,default_flow_style=False));
    newFile.close()
    print fileName + " created"

    # get all profiles so that i can determine the type of profile it is
    profileLibrary = f5Connect(appliance, username, password, '/mgmt/tm/ltm/profile/', "GET" )
    profileLibrary = profileLibrary.json()['items']
    profilePaths = []
    for profilePath in profileLibrary:
        path = profilePath['reference']['link'].replace("localhost", appliance)
        pathResponse = requests.get(path, auth=(username, password),headers=headers, verify=False)
        if "items" in pathResponse.json():
            pathResponse = pathResponse.json()['items']
            for ppath in pathResponse:
                kind = ppath['kind'].split(':')
                profilePaths.append({ "name": ppath['name'], "partition": ppath['partition'], "kind": kind[3], "content": ppath})


    for profile in profilesJson:
        for searchProfile in profilePaths:
            if searchProfile['name'] == profile['name'] and searchProfile['partition'] == profile['partition']:
                if ("defaultsFrom" in searchProfile['content']) and (searchProfile['kind'] != "server-ssl"):
                    profileJson = searchProfile['content']
                    fileName = profileJson["name"].replace(".", "_") + ".yml"
                    profileYaml = { profileJson["name"].replace(".", "_") : profileJson }
                    if not os.path.exists("../f5_vars/"+ searchProfile['kind'] +"-profile/"):
                        os.makedirs("../f5_vars/"+ searchProfile['kind'] +"-profile/")
                    newFile = open("../f5_vars/"+ searchProfile['kind'] +"-profile/" + fileName, "wb")
                    newFile.write(yaml.safe_dump(profileYaml,default_flow_style=False));
                    newFile.close()
                    print fileName + " created"

    # write the pool if one exists
    if "pool" in vipResponseJson:
        if vipResponseJson["pool"]:
            pool = vipResponseJson["pool"].split("/")
            poolResponse = poolYamlr(pool[2], pool[1], appliance, username, password)

    # write irules if they are applied to the vip
    if "rules" in vipResponseJson:
        if vipResponseJson["rules"]:
            for irule in vipResponseJson["rules"]:
                irule = irule.split("/")
                iruleResponse = iruleYamlr(irule[2], irule[1], appliance, username, password)
    return vipResponse
