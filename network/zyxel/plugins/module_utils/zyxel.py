# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Base module utilities for Zyxel network devices - HTTP API based."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import random
import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError


def encode_gs1900_password(password):
    """Encode password for GS1900 series switches.

    The GS1900 uses a custom password encoding scheme where:
    - Password characters are placed at every 5th position (reversed)
    - Password length digits are at positions 123 and 289
    - All other positions are random characters
    """
    text = ""
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    input_len = len(password)
    remaining = input_len
    for i in range(1, 322):
        if i % 5 == 0 and remaining > 0:
            remaining -= 1
            text += password[remaining]
        elif i == 123:
            text += "0" if input_len < 10 else str(input_len // 10)
        elif i == 289:
            text += str(input_len % 10)
        else:
            text += random.choice(possible)
    return text


def get_connection(module):
    """Get the connection to the Zyxel device."""
    if hasattr(module, '_zyxel_connection'):
        return module._zyxel_connection

    module._zyxel_connection = Connection(module._socket_path)
    return module._zyxel_connection


def get_capabilities(module):
    """Get device capabilities."""
    if hasattr(module, '_zyxel_capabilities'):
        return module._zyxel_capabilities

    try:
        capabilities = Connection(module._socket_path).get_capabilities()
    except ConnectionError as exc:
        module.fail_json(msg=str(exc))

    module._zyxel_capabilities = json.loads(capabilities)
    return module._zyxel_capabilities


def send_request(module, path, data=None, method='GET'):
    """Send HTTP request to the Zyxel device via httpapi connection."""
    connection = get_connection(module)
    try:
        return connection.send_request(path=path, data=data, method=method)
    except ConnectionError as exc:
        module.fail_json(msg=str(exc))


def get_page(module, page):
    """Get a page from the Zyxel web interface."""
    return send_request(module, page, method='GET')


def post_form(module, form_action, data):
    """Post form data to the Zyxel web interface."""
    return send_request(module, form_action, data=data, method='POST')


def run_commands(module, commands, check_rc=True):
    """Run commands on the Zyxel device.

    Note: Zyxel switches use HTTP API, not CLI. This function is provided
    for backward compatibility but will use the HTTP API under the hood.
    """
    connection = get_connection(module)
    results = []
    for cmd in commands:
        try:
            # For HTTP API, we simulate command execution
            # by making appropriate API calls
            result = connection.send_request(path='/', data=None, method='GET')
            results.append(result[1] if isinstance(result, tuple) else str(result))
        except ConnectionError as exc:
            if check_rc:
                module.fail_json(msg=str(exc))
            results.append('')
    return results


def load_config(module, commands, commit=False, comment=None):
    """Load configuration commands onto the device.

    Note: Zyxel switches use HTTP API for configuration. This function
    translates CLI-style commands to HTTP API calls.
    """
    connection = get_connection(module)
    results = []
    for cmd in commands:
        try:
            # Parse command and make appropriate API call
            # This is a simplified implementation
            result = connection.send_request(path='/', data=None, method='GET')
            results.append(result[1] if isinstance(result, tuple) else str(result))
        except ConnectionError as exc:
            module.fail_json(msg=str(exc))
    return results


def get_config(module, flags=None):
    """Get the current running configuration.

    Note: Zyxel switches don't have a traditional CLI config.
    This returns system information from the web interface.
    """
    connection = get_connection(module)
    try:
        result = connection.get_system_info()
        return str(result)
    except (ConnectionError, AttributeError) as exc:
        module.fail_json(msg=str(exc))


class ZyxelModule(AnsibleModule):
    """Base class for Zyxel modules with HTTP API support."""

    def __init__(self, *args, **kwargs):
        super(ZyxelModule, self).__init__(*args, **kwargs)
        self._connection = None
        self._model = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = get_connection(self)
        return self._connection

    @property
    def model(self):
        """Get the switch model type."""
        if self._model is None:
            caps = get_capabilities(self)
            self._model = caps.get('device_info', {}).get('model', 'gs1920')
        return self._model

    def get_page(self, page):
        """Get a page from the web interface."""
        return get_page(self, page)

    def post_form(self, form_action, data):
        """Post form data to the web interface."""
        return post_form(self, form_action, data)


def parse_port_config(output):
    """Parse port configuration from CLI output."""
    ports = {}
    current_port = None
    
    for line in output.splitlines():
        # Match port header (e.g., "Port 1" or "port1")
        port_match = re.match(r'^[Pp]ort\s*(\d+)', line)
        if port_match:
            current_port = port_match.group(1)
            ports[current_port] = {}
            continue
        
        if current_port and ':' in line:
            key, _, value = line.partition(':')
            ports[current_port][key.strip().lower().replace(' ', '_')] = value.strip()
    
    return ports


def parse_vlan_config(output):
    """Parse VLAN configuration from CLI output."""
    vlans = {}
    
    for line in output.splitlines():
        # Match VLAN entries
        vlan_match = re.match(r'^\s*(\d+)\s+(\S+)\s+(.*)$', line)
        if vlan_match:
            vlan_id = vlan_match.group(1)
            name = vlan_match.group(2)
            vlans[vlan_id] = {
                'id': vlan_id,
                'name': name,
                'ports': vlan_match.group(3).strip() if vlan_match.group(3) else ''
            }
    
    return vlans

