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
  - Configure management services including SNMP, cloud/Nebula, and service control via HTTP API.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  snmp:
    description:
      - SNMP configuration.
    type: dict
    suboptions:
      get_community:
        description: SNMP read community string.
        type: str
      set_community:
        description: SNMP write community string.
        type: str
      trap_community:
        description: SNMP trap community string.
        type: str
      version:
        description: SNMP version (v1, v2c, v3).
        type: str
        choices: ['v1', 'v2c', 'v3']
  cloud:
    description:
      - Cloud/Nebula configuration.
    type: dict
    suboptions:
      discovery_enabled:
        description: Enable or disable Nebula discovery.
        type: bool
  service_control:
    description:
      - Service control configuration (enable/disable management services).
    type: dict
    suboptions:
      snmp:
        description: Enable SNMP service.
        type: bool
      telnet:
        description: Enable Telnet service.
        type: bool
      ssh:
        description: Enable SSH service.
        type: bool
      http:
        description: Enable HTTP service.
        type: bool
      https:
        description: Enable HTTPS service.
        type: bool
notes:
  - Tested against Zyxel GS1900, GS1915, and GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure SNMP with public read and private write
  network.zyxel.zyxel_management:
    snmp:
      get_community: "public"
      set_community: "private"
      trap_community: "public"
      version: "v2c"

- name: Disable Nebula cloud discovery
  network.zyxel.zyxel_management:
    cloud:
      discovery_enabled: false

- name: Enable SNMP service and disable Telnet
  network.zyxel.zyxel_management:
    service_control:
      snmp: true
      telnet: false
      ssh: true
      https: true
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
  sample: true
snmp:
  description: SNMP configuration result
  returned: when snmp is configured
  type: dict
  sample: {"success": true, "message": "SNMP configured"}
cloud:
  description: Cloud/Nebula configuration result
  returned: when cloud is configured
  type: dict
  sample: {"success": true, "message": "Cloud/Nebula configured"}
service_control:
  description: Service control configuration result
  returned: when service_control is configured
  type: dict
  sample: {"success": true, "message": "Service control configured"}
'''

from ansible.module_utils.basic import AnsibleModule


def configure_snmp(module, config):
    """Configure SNMP settings via httpapi."""
    from ansible_collections.network.zyxel.plugins.module_utils.zyxel import get_connection
    try:
        connection = get_connection(module)
        return connection.configure_snmp(config)
    except Exception as e:
        return False, 'Failed to configure SNMP: %s' % str(e)


def configure_cloud(module, config):
    """Configure cloud/Nebula settings via httpapi."""
    from ansible_collections.network.zyxel.plugins.module_utils.zyxel import get_connection
    try:
        connection = get_connection(module)
        return connection.configure_cloud(config)
    except Exception as e:
        return False, 'Failed to configure cloud: %s' % str(e)


def configure_service_control(module, config):
    """Configure service control settings via httpapi."""
    from ansible_collections.network.zyxel.plugins.module_utils.zyxel import get_connection
    try:
        connection = get_connection(module)
        return connection.configure_service_control(config)
    except Exception as e:
        return False, 'Failed to configure service control: %s' % str(e)


def main():
    """Main module execution."""
    argument_spec = dict(
        snmp=dict(type='dict'),
        cloud=dict(type='dict'),
        service_control=dict(type='dict'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {
        'changed': False,
    }

    # Configure SNMP
    if module.params.get('snmp'):
        snmp_config = module.params['snmp']

        if module.check_mode:
            result['snmp'] = {'success': True, 'message': 'Would configure SNMP'}
            result['changed'] = True
        else:
            success, message = configure_snmp(module, snmp_config)
            result['snmp'] = {'success': success, 'message': message}
            if success:
                result['changed'] = True
            else:
                module.fail_json(msg=message, **result)

    # Configure Cloud/Nebula
    if module.params.get('cloud'):
        cloud_config = module.params['cloud']

        if module.check_mode:
            result['cloud'] = {'success': True, 'message': 'Would configure cloud'}
            result['changed'] = True
        else:
            success, message = configure_cloud(module, cloud_config)
            result['cloud'] = {'success': success, 'message': message}
            if success:
                result['changed'] = True
            else:
                module.fail_json(msg=message, **result)

    # Configure Service Control
    if module.params.get('service_control'):
        svc_config = module.params['service_control']

        if module.check_mode:
            result['service_control'] = {'success': True, 'message': 'Would configure services'}
            result['changed'] = True
        else:
            success, message = configure_service_control(module, svc_config)
            result['service_control'] = {'success': success, 'message': message}
            if success:
                result['changed'] = True
            else:
                module.fail_json(msg=message, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

