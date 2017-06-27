#!/bin/python
from __future__ import division

import bitmath
import requests
import json
import sys
import argparse

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import HTTPError


def check_node():
	# Parse da args
	parser = argparse.ArgumentParser()
	parser.add_argument('-m', '--master', help='Master url', required=True)
	parser.add_argument('-n', '--node', help='Node name in the cluster', required=True)
	parser.add_argument('-t', '--token', help='Authentication token', required=True)
	args = parser.parse_args()


	# Mute the SSL warnings... because we know that bad things occur
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

	error_msg = "An HTTP error has occured: "

	# Headers
	headers = {'Authorization': 'Bearer {0}'.format(args.token)}


	# get the node stats
	r = requests.get('{0}/api/v1/nodes/{1}'.format(args.master, args.node), verify=False, headers=headers)

	try:
	    r.raise_for_status()
	except HTTPError as e:
	    print "{0}{1}".format(error_msg, e)
	    sys.exit(1)


	# Parse out our stats
	node_cpu = int(r.json()['status']['capacity']['cpu'])
	node_mem = bitmath.parse_string(r.json()['status']['capacity']['memory'] + 'B')


	# get pod specific info for the node
	r = requests.get('{0}/api/v1/pods?fieldSelector=spec.nodeName%3D{1}%2Cstatus.phase%21%3DFailed%2Cstatus.phase%21%3DSucceeded'.format(args.master, args.node), verify=False, headers=headers)

	try:
	    r.raise_for_status()
	except HTTPError as e:
	    print "{0}{1}".format(error_msg, e)
	    sys.exit(1)

	# Make some empty lists
	req_mem = []
	req_cpu = []


	# Let the magic start
	for x in r.json()['items']:
	    
	    for container in x['spec']['containers']:
	      data = container['resources']
	      if data:
		  req_val = data['requests']
		  mem_val = req_val.get('memory', '0')
		  cpu_val = req_val.get('cpu', '0')
		  # CPU needs an If because millicores is not a real unit and we need to convert it to a float 
		  if 'm' in cpu_val:
		      cpu_val = int(cpu_val.replace('m', '')) / 1000
		  else:
		      cpu_val = int(cpu_val)
		  req_cpu.append(cpu_val)
		  # Memory
                  p_mem = bitmath.parse_string(mem_val + 'B')
		  req_mem.append(p_mem.MB)
                    


	# Sum them up
	total_req_mem = sum(req_mem)
	total_req_cpu = sum(req_cpu)


	# Get percent of
	print round((100 * int(total_req_mem) / int(node_mem.MB)), 2)

if __name__ == '__main__':
  check_node()
