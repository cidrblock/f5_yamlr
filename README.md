Python script to pull all information about a Virtual Server from an F5

Usage

```shell
➜  f5_yamlr virtualenv venv
New python executable in /Users/bthornto/github/f5_yamlr/venv/bin/python
Installing setuptools, pip, wheel...done.

➜  f5_yamlr source venv/bin/activate
(venv) ➜  f5_yamlr pip install -r requirements.txt
Requirement already satisfied: appdirs==1.4.0 in ./venv/lib/python2.7/site-packages (from -r requirements.txt (line 1))
Collecting jsonify==0.5 (from -r requirements.txt (line 2))
Requirement already satisfied: packaging==16.8 in ./venv/lib/python2.7/site-packages (from -r requirements.txt (line 3))
Collecting pyaml==16.12.2 (from -r requirements.txt (line 4))
  Using cached pyaml-16.12.2-py2.py3-none-any.whl
Requirement already satisfied: pyparsing==2.1.10 in ./venv/lib/python2.7/site-packages (from -r requirements.txt (line 5))
Collecting PyYAML==3.12 (from -r requirements.txt (line 6))
Collecting requests==2.13.0 (from -r requirements.txt (line 7))
  Using cached requests-2.13.0-py2.py3-none-any.whl
Requirement already satisfied: six==1.10.0 in ./venv/lib/python2.7/site-packages (from -r requirements.txt (line 8))
Installing collected packages: jsonify, PyYAML, pyaml, requests
Successfully installed PyYAML-3.12 jsonify-0.5 pyaml-16.12.2 requests-2.13.0

(venv) ➜  f5_yamlr

(venv) ➜  cd scripts

(venv) ➜  scripts git:(master) ✗ python go.py -h
usage: go.py [-h] -vs VS -pt PARTITION -b BIG -u USERNAME -p PASSWORD

Dumps bigIP virtual server etc to yaml

optional arguments:
  -h, --help            show this help message and exit
  -vs VS, --virtual_server VS
                        The name of the virtual server to dump.
  -pt PARTITION, --partition PARTITION
                        The name of the parition the virtual server is in.
  -b BIG, --bigip BIG   The fqdn of the bigIP.
  -u USERNAME, --username USERNAME
                        The username.
  -p PASSWORD, --password PASSWORD
                        The password.

(venv) ➜  scripts git:(master) ✗ python go.py -vs ntp.company.net -pt network -b f5.company.net -u admin -p 'password'
ntp_company_net.yml created
server1_company_net.yml created
server2_company_net.yml created
ntp_starbucks_net_pool.yml created
gateway_icmp.yml created
done
(venv) ➜  scripts git:(master) ✗
```
