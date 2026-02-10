#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Network Automation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gnmi_get
short_description: Retrieve data from network devices using gNMI with OpenConfig
version_added: "1.0.0"
description:
  - Retrieve configuration and state data from network devices using gNMI protocol
  - Supports OpenConfig models natively via pygnmi
author:
  - Network Automation Team
options:
  host:
    description:
      - IP address or hostname of the target device
    required: true
    type: str
  port:
    description:
      - gNMI port number
    required: false
    type: int
    default: 57400
  username:
    description:
      - Username for authentication
    required: true
    type: str
  password:
    description:
      - Password for authentication
    required: true
    type: str
  path:
    description:
      - OpenConfig or YANG path to retrieve data from
      - Can be a single path string or list of paths
    required: true
    type: raw
  insecure:
    description:
      - Skip TLS certificate validation
    required: false
    type: bool
    default: true
'''

EXAMPLES = r'''
# Get all interfaces using OpenConfig
- name: Retrieve interface information
  gnmi_get:
    host: "{{ ansible_host }}"
    port: 57400
    username: admin
    password: secret
    path: "openconfig-interfaces:interfaces/interface"

# Get specific configuration
- name: Get BGP configuration
  gnmi_get:
    host: 192.168.1.1
    port: 57400
    username: admin
    password: secret
    path: "openconfig-bgp:bgp"
'''

RETURN = r'''
response:
  description: The gNMI Get response
  returned: always
  type: dict
  sample: {
    "notification": [
      {
        "update": [
          {
            "path": "openconfig-interfaces:interfaces/interface",
            "val": {...}
          }
        ]
      }
    ]
  }
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from pygnmi.client import gNMIclient
    HAS_PYGNMI = True
except ImportError:
    HAS_PYGNMI = False


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        port=dict(type='int', required=False, default=57400),
        username=dict(type='str', required=True, no_log=True),
        password=dict(type='str', required=True, no_log=True),
        path=dict(type='raw', required=True),
        insecure=dict(type='bool', required=False, default=True),
    )

    result = dict(
        changed=False,
        response={},
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PYGNMI:
        module.fail_json(msg='pygnmi is required. Install with: pip install pygnmi')

    # Extract parameters
    host = module.params['host']
    port = module.params['port']
    username = module.params['username']
    password = module.params['password']
    path = module.params['path']
    insecure = module.params['insecure']

    # Ensure path is a list
    if isinstance(path, str):
        path = [path]

    try:
        # Create gNMI connection
        connection = gNMIclient(
            target=(host, port),
            username=username,
            password=password,
            insecure=insecure
        )
        connection.connect()

        # Execute gNMI Get
        response = connection.get(path=path, encoding='json_ietf')
        
        # Close connection
        connection.close()

        result['response'] = response
        result['changed'] = False

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f'gNMI Get failed: {str(e)}', **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
