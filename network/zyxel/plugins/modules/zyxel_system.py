# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for system configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_system
short_description: Configure system settings on Zyxel switches
description:
  - Configure system-level settings including hostname, location, contact via web interface.
  - Also supports NTP server configuration and timezone settings.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  hostname:
    description:
      - System hostname/name.
    type: str
  location:
    description:
      - System location (SNMP sysLocation).
    type: str
  contact:
    description:
      - System contact (SNMP sysContact).
    type: str
  ntp_servers:
    description:
      - List of NTP server addresses (up to 3 servers supported).
    type: list
    elements: str
  timezone:
    description:
      - Timezone setting (e.g., 'UTC', 'UTC-5', 'UTC+8').
    type: str
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure system settings
  network.zyxel.zyxel_system:
    hostname: "switch-core-01"
    location: "Data Center Rack 5"
    contact: "admin@example.com"

- name: Configure NTP servers
  network.zyxel.zyxel_system:
    ntp_servers:
      - "pool.ntp.org"
      - "time.google.com"
    timezone: "UTC-5"

- name: Configure all system settings
  network.zyxel.zyxel_system:
    hostname: "switch-core-01"
    location: "Data Center Rack 5"
    contact: "admin@example.com"
    ntp_servers:
      - "pool.ntp.org"
    timezone: "UTC"
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
config:
  description: Configuration applied to the device
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
    send_request,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        hostname=dict(type='str'),
        location=dict(type='str'),
        contact=dict(type='str'),
        ntp_servers=dict(type='list', elements='str'),
        timezone=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'config': {}}
    config = {}

    if module.params.get('hostname'):
        config['hostname'] = module.params['hostname']

    if module.params.get('location'):
        config['location'] = module.params['location']

    if module.params.get('contact'):
        config['contact'] = module.params['contact']

    if module.params.get('ntp_servers'):
        config['ntp_servers'] = module.params['ntp_servers']

    if module.params.get('timezone'):
        config['timezone'] = module.params['timezone']

    if config:
        result['changed'] = True
        result['config'] = config
        if not module.check_mode:
            connection = get_connection(module)
            connection.configure_system(config)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

