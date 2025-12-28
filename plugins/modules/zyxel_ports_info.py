# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for gathering port information from Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_ports_info
short_description: Gather port information from Zyxel switches
description:
  - Retrieves current port configuration and status via web interface.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  ports:
    description:
      - List of specific ports to gather info for.
      - If not specified, returns info for all ports.
    type: list
    elements: str
    required: false
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Get all port information
  network.zyxel.zyxel_ports_info:
  register: ports_info

- name: Get specific ports information
  network.zyxel.zyxel_ports_info:
    ports:
      - "1"
      - "2"
      - "3"
  register: ports_info

- name: Display port info
  debug:
    var: ports_info.ports
'''

RETURN = r'''
ports:
  description: Dictionary of port configurations keyed by port name
  returned: always
  type: dict
  sample:
    "1":
      enabled: true
      name: "Uplink"
      speed: "auto"
    "2":
      enabled: true
      name: ""
      speed: "auto"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        ports=dict(type='list', elements='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'ports': {}}
    requested_ports = module.params.get('ports')

    connection = get_connection(module)
    all_ports = connection.get_ports_info()

    if requested_ports:
        for port in requested_ports:
            if port in all_ports:
                result['ports'][port] = all_ports[port]
    else:
        result['ports'] = all_ports

    module.exit_json(**result)


if __name__ == '__main__':
    main()

