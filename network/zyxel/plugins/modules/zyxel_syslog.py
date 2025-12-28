# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch syslog settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_syslog
short_description: Manage syslog settings on Zyxel switches
description:
  - This module manages syslog server configuration on Zyxel switches via HTTP API.
  - Configure remote syslog servers.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  enabled:
    description:
      - Enable or disable syslog globally.
    type: bool
    default: true
  server:
    description:
      - IP address or hostname of a single syslog server.
    type: str
  servers:
    description:
      - List of syslog servers.
      - Each item can be a string (address) or dict with address and port.
    type: list
    elements: raw
  port:
    description:
      - UDP port for syslog server (used with single server parameter).
    type: int
    default: 514
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure single syslog server
  network.zyxel.zyxel_syslog:
    enabled: true
    server: "192.168.1.100"
    port: 514

- name: Configure multiple syslog servers
  network.zyxel.zyxel_syslog:
    enabled: true
    servers:
      - address: "192.168.1.100"
        port: 514
      - address: "192.168.1.101"

- name: Disable syslog
  network.zyxel.zyxel_syslog:
    enabled: false
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
config:
  description: Configuration applied to the device.
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
        enabled=dict(type='bool', default=True),
        server=dict(type='str'),
        servers=dict(type='list', elements='raw'),
        port=dict(type='int', default=514),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['server', 'servers']],
    )

    result = {'changed': False, 'config': {}}

    config = {
        'enabled': module.params.get('enabled', True),
    }

    # Build servers list
    servers = []
    if module.params.get('servers'):
        for srv in module.params['servers']:
            if isinstance(srv, dict):
                servers.append(srv)
            else:
                servers.append({'address': srv, 'port': 514})
    elif module.params.get('server'):
        servers.append({
            'address': module.params['server'],
            'port': module.params.get('port', 514)
        })

    if servers:
        config['servers'] = servers

    result['config'] = config

    if not module.check_mode:
        connection = get_connection(module)
        success, message = connection.configure_syslog(config)
        if success:
            result['changed'] = True
            result['message'] = message
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
