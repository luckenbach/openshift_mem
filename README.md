# Memory reservation monitor for Openshift

## Why
Needed a way to check the reservation reported back from openshift nodes

## How
APIs

## Installation
pip install -r requirements.txt

# Preparing OpenShift

* Install the following RPMs from the EPEL repo
  * `yum install python-requests`
  * `yum install python2-bitmath`
* Copy the file ./monitor.py into `/usr/local/bin` and `chmod +x /usr/local/bin/monitor.py`
* As a user with cluster-admin permissions:
  * Create a service account to use
    * `oc create sa zabbix -n default`
  * Grant `cluster-reader` permission to the service account
    * `oc adm policy add-cluster-role-to-user cluster-reader system:serviceaccount:default:zabbix -n default`
  * Retrieve the token from the service account
    * `oc get sa zabbix -o yaml -n default`
  * Find the name of the secret that contains the token (e.g. `zabbix-token-7gp29`)
    * `oc get secret zabbix-token-7gp29  -o yaml`
  * Find the `token:` and decode it:
    * `base64 --decode <token>`
  * Test the monitor:
    * `/usr/local/bin/monitor.py -m <Master-URL> -n <Internal Node Name> -t <Decoded Token>`
