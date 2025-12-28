# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for management services on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_management
short_description: Configure management services on Zyxel switches
description:
  - Configure management services including SNMP, syslog, HTTPS, SSH, and Telnet via HTTP API.
  - Note: HTTP API management configuration is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  snmp:
    description:
      - SNMP configuration.
    type: dict
  syslog:
    description:
      - Syslog configuration.
    type: dict
  ntp:
    description:
      - NTP configuration.
    type: dict
  https:
    description:
      - HTTPS management configuration.
    type: dict
  ssh:
    description:
      - SSH configuration.
    type: dict
  telnet:
    description:
      - Telnet configuration.
    type: dict
  http:
    description:
      - HTTP management configuration.
    type: dict
notes:
  - HTTP API management configuration is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure management services
  network.zyxel.zyxel_management:
    snmp:
      enabled: true
      community_read: "public"
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
  sample: false
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """Main module execution."""
    argument_spec = dict(
        snmp=dict(type='dict'),
        syslog=dict(type='dict'),
        ntp=dict(type='dict'),
        https=dict(type='dict'),
        ssh=dict(type='dict'),
        telnet=dict(type='dict'),
        http=dict(type='dict'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API management configuration not yet implemented
    module.fail_json(
        msg="Management configuration via HTTP API is not yet implemented for GS1920 series. "
            "Please configure management services through the web interface."
    )


if __name__ == '__main__':
    main()

