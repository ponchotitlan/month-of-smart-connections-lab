#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Network Automation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gnmi_set
short_description: Configure network devices using gNMI with OpenConfig
version_added: "1.0.0"
description:
  - Configure network devices using gNMI Set operations
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
  update:
    description:
      - List of tuples (path, value) for gNMI Set update operation
      - Path is the OpenConfig/YANG path, value is the configuration data
    required: false
    type: list
    elements: dict
  replace:
    description:
      - List of tuples (path, value) for gNMI Set replace operation
    required: false
    type: list
    elements: dict
  delete:
    description:
      - List of paths to delete
    required: false
    type: list
    elements: str
  insecure:
    description:
      - Skip TLS certificate validation
    required: false
    type: bool
    default: true
'''

EXAMPLES = r'''
# Configure interface using OpenConfig
- name: Configure interface
  gnmi_set:
    host: "{{ ansible_host }}"
    port: 57400
    username: admin
    password: secret
    update:
      - path: "openconfig-interfaces:interfaces/interface"
        value:
          name: "GigabitEthernet0/0/0/1"
          config:
            name: "GigabitEthernet0/0/0/1"
            description: "Configured by Ansible"
            enabled: true

# Delete configuration
- name: Delete interface description
  gnmi_set:
    host: 192.168.1.1
    port: 57400
    username: admin
    password: secret
    delete:
      - "openconfig-interfaces:interfaces/interface[name=GigabitEthernet0/0/0/1]/config/description"
'''

RETURN = r'''
response:
  description: The gNMI Set response
  returned: always
  type: dict
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
        update=dict(type='list', elements='dict', required=False, default=[]),
        replace=dict(type='list', elements='dict', required=False, default=[]),
        delete=dict(type='list', elements='str', required=False, default=[]),
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
    update_list = module.params['update']
    replace_list = module.params['replace']
    delete_list = module.params['delete']
    insecure = module.params['insecure']

    # Check if at least one operation is specified
    if not (update_list or replace_list or delete_list):
        module.fail_json(msg='At least one of update, replace, or delete must be specified')

    if module.check_mode:
        module.exit_json(**result)

    try:
        # Create gNMI connection
        connection = gNMIclient(
            target=(host, port),
            username=username,
            password=password,
            insecure=insecure
        )
        connection.connect()

        # Convert update/replace dicts to tuples for pygnmi
        update_tuples = [(item['path'], item['value']) for item in update_list] if update_list else None
        replace_tuples = [(item['path'], item['value']) for item in replace_list] if replace_list else None

        # Execute gNMI Set
        response = connection.set(
            update=update_tuples,
            replace=replace_tuples,
            delete=delete_list if delete_list else None,
            encoding='json_ietf'
        )
        
        # Close connection
        connection.close()

        result['response'] = response
        result['changed'] = True

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f'gNMI Set failed: {str(e)}', **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
