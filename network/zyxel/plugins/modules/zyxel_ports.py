# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for bulk port configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_ports
short_description: Bulk configure ports on Zyxel switches
description:
  - Configure multiple ports at once using a dictionary of port configurations via HTTP API.
  - Each port can have its own settings for state, speed, and description.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  ports:
    description:
      - Dictionary of port configurations keyed by port number.
      - Each port configuration can include enabled, speed, and name (description).
    type: dict
    required: true
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure multiple ports
  network.zyxel.zyxel_ports:
    ports:
      "1":
        enabled: true
        speed: auto
        name: "Uplink to Core"
      "2":
        enabled: true
        speed: 1g-full
      "3":
        enabled: false

- name: Bulk configure access ports
  network.zyxel.zyxel_ports:
    ports:
      "5":
        enabled: true
        name: "Workstation 1"
      "6":
        enabled: true
        name: "Workstation 2"
      "7":
        enabled: true
        name: "Printer"
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
ports_configured:
  description: List of ports that were configured
  returned: always
  type: list
  sample: ["1", "2", "3"]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        ports=dict(type='dict', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'ports_configured': []}
    ports = module.params['ports']

    if not module.check_mode:
        connection = get_connection(module)
        for port_id, config in ports.items():
            if config:
                port_config = {
                    'enabled': config.get('enabled', True),
                }
                if config.get('speed'):
                    port_config['speed'] = config['speed']
                if config.get('name'):
                    port_config['name'] = config['name']

                response = connection.configure_port(port_id, port_config)
                if response:
                    result['changed'] = True
                    result['ports_configured'].append(port_id)
    else:
        result['changed'] = True
        result['ports_configured'] = list(ports.keys())

    module.exit_json(**result)


if __name__ == '__main__':
    main()

