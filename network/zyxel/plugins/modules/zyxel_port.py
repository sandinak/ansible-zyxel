# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch port settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_port
short_description: Manage port settings on Zyxel switches
description:
  - This module provides management of physical port settings on Zyxel switches.
  - Configure port state, speed, and description via HTTP API.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  name:
    description:
      - Port number to configure.
    type: str
    required: true
  state:
    description:
      - Administrative state of the port.
    type: str
    choices: ['enabled', 'disabled']
    default: 'enabled'
  speed:
    description:
      - Speed setting for the port.
      - Use 'auto' for auto-negotiation.
      - Format like '1g-full' for specific speed/duplex.
    type: str
    choices: ['auto', '10m-half', '10m-full', '100m-half', '100m-full', '1g-full']
    default: 'auto'
  description:
    description:
      - Description/name of the port.
    type: str
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Enable port 1 with auto speed
  network.zyxel.zyxel_port:
    name: "1"
    state: enabled
    speed: auto

- name: Configure port 5 with 1Gbps
  network.zyxel.zyxel_port:
    name: "5"
    speed: '1g-full'
    description: "Uplink to core switch"

- name: Disable port 10
  network.zyxel.zyxel_port:
    name: "10"
    state: disabled
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
port:
  description: The port that was configured.
  returned: always
  type: str
  sample: "1"
config:
  description: Configuration applied to the port.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', choices=['enabled', 'disabled'], default='enabled'),
        speed=dict(type='str', choices=['auto', '10m-half', '10m-full',
                                         '100m-half', '100m-full', '1g-full'],
                   default='auto'),
        description=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'port': module.params['name'], 'config': {}}

    port_id = module.params['name']
    config = {
        'enabled': module.params['state'] == 'enabled',
        'speed': module.params['speed'],
    }

    if module.params.get('description') is not None:
        config['name'] = module.params['description']

    result['config'] = config

    if not module.check_mode:
        connection = get_connection(module)
        response = connection.configure_port(port_id, config)
        if response:
            result['changed'] = True
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()

