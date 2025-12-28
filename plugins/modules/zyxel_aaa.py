# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for AAA configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_aaa
short_description: Configure AAA (RADIUS/TACACS+) on Zyxel switches
description:
  - Configure Authentication, Authorization, and Accounting settings via HTTP API.
  - Note: HTTP API AAA configuration is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  authentication_order:
    description:
      - Order of authentication methods.
    type: list
    elements: str
    choices: ['local', 'radius', 'tacacs']
  radius:
    description:
      - RADIUS server configuration.
    type: dict
  tacacs:
    description:
      - TACACS+ server configuration.
    type: dict
notes:
  - HTTP API AAA configuration is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure RADIUS authentication
  network.zyxel.zyxel_aaa:
    authentication_order:
      - radius
      - local
    radius:
      enabled: true
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
        authentication_order=dict(
            type='list',
            elements='str',
            choices=['local', 'radius', 'tacacs']
        ),
        radius=dict(type='dict'),
        tacacs=dict(type='dict'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API AAA configuration not yet implemented
    module.fail_json(
        msg="AAA configuration via HTTP API is not yet implemented for GS1920 series. "
            "Please configure AAA through the web interface."
    )


if __name__ == '__main__':
    main()

