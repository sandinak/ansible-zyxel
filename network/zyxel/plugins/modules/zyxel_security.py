# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for security configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_security
short_description: Configure security features on Zyxel switches
description:
  - Configure port security, 802.1X authentication, and other security features via HTTP API.
  - Note: HTTP API security configuration is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  port_security:
    description:
      - Port security configuration per port.
    type: dict
  dot1x:
    description:
      - 802.1X authentication configuration.
    type: dict
  dhcp_snooping:
    description:
      - DHCP snooping configuration.
    type: dict
  arp_inspection:
    description:
      - Dynamic ARP inspection configuration.
    type: dict
notes:
  - HTTP API security configuration is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure port security
  network.zyxel.zyxel_security:
    port_security:
      ports:
        "1":
          enabled: true
          max_addresses: 2
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
        port_security=dict(type='dict'),
        dot1x=dict(type='dict'),
        dhcp_snooping=dict(type='dict'),
        arp_inspection=dict(type='dict'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API security configuration not yet implemented
    module.fail_json(
        msg="Security configuration via HTTP API is not yet implemented for GS1920 series. "
            "Please configure security features through the web interface."
    )


if __name__ == '__main__':
    main()

