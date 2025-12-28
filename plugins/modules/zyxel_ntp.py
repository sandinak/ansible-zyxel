# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch NTP settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_ntp
short_description: Manage NTP settings on Zyxel switches
description:
  - This module manages NTP server configuration on Zyxel switches via HTTP API.
  - Configure up to 3 NTP servers and timezone settings.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  servers:
    description:
      - List of NTP server addresses (up to 3 servers supported).
    type: list
    elements: str
    required: true
  timezone:
    description:
      - Timezone setting (e.g., 'UTC', 'UTC-5', 'UTC+8').
    type: str
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure NTP servers
  network.zyxel.zyxel_ntp:
    servers:
      - "pool.ntp.org"
      - "time.google.com"

- name: Configure NTP with timezone
  network.zyxel.zyxel_ntp:
    servers:
      - "192.168.1.1"
    timezone: "UTC-5"

- name: Configure multiple NTP servers with timezone
  network.zyxel.zyxel_ntp:
    servers:
      - "0.pool.ntp.org"
      - "1.pool.ntp.org"
      - "2.pool.ntp.org"
    timezone: "UTC"
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
        servers=dict(type='list', elements='str', required=True),
        timezone=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'config': {}}

    config = {
        'ntp_servers': module.params['servers'],
    }

    if module.params.get('timezone'):
        config['timezone'] = module.params['timezone']

    result['config'] = config

    if not module.check_mode:
        connection = get_connection(module)
        response = connection.configure_system(config)
        if response:
            result['changed'] = True
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()

