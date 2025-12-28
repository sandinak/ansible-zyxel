# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Zyxel HTTP API Plugin for GS1900/GS1915/GS1920 series switches.

This plugin provides HTTP-based configuration management for Zyxel switches
that expose their configuration via web interface.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
author: Ansible Networking Team
httpapi: zyxel
short_description: HttpApi Plugin for Zyxel GS1900/GS1915/GS1920 switches
description:
  - This HttpApi plugin provides methods to interact with Zyxel switches
    via their web interface.
  - Supports GS1900, GS1915, and GS1920 series switches.
  - Handles different authentication methods for each switch type.
version_added: "1.2.0"
options:
  zyxel_model:
    type: str
    description:
      - The Zyxel switch model type.
      - If not specified, will be auto-detected from the login page.
    choices: ['gs1900', 'gs1915', 'gs1920']
    vars:
      - name: ansible_zyxel_model
      - name: zyxel_model
"""

import json
import random
import re
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from ansible.plugins.httpapi import HttpApiBase
from ansible.module_utils.basic import to_text


def encode_gs1900_password(password):
    """Encode password for GS1900 series switches."""
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


class HttpApi(HttpApiBase):
    """HttpApi plugin for Zyxel switches supporting GS1900/GS1915/GS1920."""

    def __init__(self, connection):
        super(HttpApi, self).__init__(connection)
        self.connection = connection
        self._model = None
        self._firmware_version = None
        self._auth_id = None  # For GS1900 token-based auth
        self._logged_in = False

    def detect_model(self):
        """Detect switch model from the login page."""
        if self._model:
            return self._model

        # Check if model is set via variable
        model_var = self.get_option('zyxel_model')
        if model_var:
            self._model = model_var.lower()
            return self._model

        # Try to detect from login page
        try:
            response, response_data = self.connection.send('/', None, method='GET')
            content = to_text(response_data.getvalue())

            if 'GS1900' in content:
                self._model = 'gs1900'
            elif 'GS1915' in content:
                self._model = 'gs1915'
            elif 'GS1920' in content:
                self._model = 'gs1920'
            else:
                # Default to gs1920 form-based auth
                self._model = 'gs1920'
        except Exception:
            self._model = 'gs1920'

        return self._model

    def get_firmware_version(self):
        """Get firmware version from the switch.
        
        Returns:
            String firmware version (e.g., 'V1.15', 'V1.16', 'V2.70')
        """
        if self._firmware_version:
            return self._firmware_version
        
        try:
            # Get system info which includes firmware version
            info = self.get_system_info()
            self._firmware_version = info.get('firmware', '')
            return self._firmware_version
        except Exception:
            return ''

    def _compare_firmware_version(self, version1, version2):
        """Compare two firmware version strings.
        
        Args:
            version1: First version string (e.g., 'V1.15', 'V2.70')
            version2: Second version string (e.g., 'V1.16', 'V2.70')
            
        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        # Extract numeric parts from versions like 'V1.15' -> [1, 15]
        def parse_version(v):
            # Remove 'V' prefix if present and split by '.'
            v = v.upper().strip()
            if v.startswith('V'):
                v = v[1:]
            try:
                return [int(x) for x in v.split('.')]
            except (ValueError, AttributeError):
                return [0]
        
        parts1 = parse_version(version1)
        parts2 = parse_version(version2)
        
        # Pad shorter version with zeros
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        # Compare each part
        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        return 0

    def send_request(self, path, data=None, **kwargs):
        """Send an HTTP request to the device."""
        method = kwargs.get('method', 'GET')
        headers = kwargs.get('headers', {})

        if data and method == 'POST':
            if isinstance(data, (dict, list)):
                # urlencode handles both dict and list of tuples
                data = urlencode(data)
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response, response_data = self.connection.send(
            path,
            data,
            method=method,
            headers=headers
        )

        return response.getcode(), to_text(response_data.getvalue())

    def login(self, username, password):
        """Login to the Zyxel switch web interface."""
        model = self.detect_model()

        if model == 'gs1900':
            self._login_gs1900(username, password)
        elif model == 'gs1915':
            self._login_gs1915(username, password)
        else:  # gs1920
            self._login_gs1920(username, password)

        self._logged_in = True

    def _login_gs1920(self, username, password):
        """Login for GS1920 series (form-based with specific field names)."""
        payload = {
            'rpAuthForm_Ipt_UserName': username,
            'rpAuthForm_Ipt_Password': password
        }
        code, response = self.send_request('/Forms/login_1', payload, method='POST')
        if code not in [200, 302, 303]:
            raise Exception('Failed to login to GS1920: HTTP %d' % code)

    def _login_gs1915(self, username, password):
        """Login for GS1915 series (form-based with different field names)."""
        payload = {
            'rpAuthForm_IptTextUsername': username,
            'rpAuthForm_IptTextPassword': password
        }
        code, response = self.send_request('/Forms/login_1', payload, method='POST')
        if code not in [200, 302, 303]:
            raise Exception('Failed to login to GS1915: HTTP %d' % code)

    def _login_gs1900(self, username, password):
        """Login for GS1900 series (CGI-based with encoded password)."""
        encoded_pw = encode_gs1900_password(password)
        payload = {
            'username': username,
            'password': encoded_pw,
            'login': 'true'
        }
        code, response = self.send_request('/cgi-bin/dispatcher.cgi', payload, method='POST')
        if code != 200:
            raise Exception('Failed to login to GS1900: HTTP %d' % code)

        self._auth_id = response.strip()

        # Verify login
        verify_payload = {'authId': self._auth_id, 'login_chk': 'true'}
        code, response = self.send_request('/cgi-bin/dispatcher.cgi', verify_payload, method='POST')
        if 'OK' not in response:
            raise Exception('GS1900 login verification failed')

    def logout(self):
        """Logout from the switch."""
        # Zyxel doesn't require explicit logout, session expires
        self._logged_in = False
        self._auth_id = None

    def get_page(self, page):
        """Get a page from the web interface."""
        model = self.detect_model()

        if model == 'gs1900':
            # GS1900 uses cmd parameter
            if isinstance(page, int):
                path = '/cgi-bin/dispatcher.cgi?cmd=%d' % page
            else:
                path = page
        else:
            path = page

        code, response = self.send_request(path, method='GET')
        if code == 200:
            return response
        raise Exception('Failed to get page %s: HTTP %d' % (page, code))

    def post_form(self, form_action, data):
        """Post form data to the web interface."""
        model = self.detect_model()

        if model == 'gs1900':
            # GS1900 uses dispatcher.cgi
            if 'cmd' not in data:
                data['cmd'] = form_action if isinstance(form_action, int) else 0
            path = '/cgi-bin/dispatcher.cgi'
        else:
            path = form_action

        code, response = self.send_request(path, data, method='POST')
        return code, response

    def _get_gs1900_xssid(self, cmd):
        """Get XSSID token from a GS1900 form page.

        Args:
            cmd: The command number for the form page

        Returns:
            XSSID token string or None if not found
        """
        content = self.get_page(cmd)
        match = re.search(r'name="XSSID"\s+value="([^"]+)"', content)
        if match:
            return match.group(1)
        return None

    def get_system_info(self):
        """Get system information from the switch."""
        model = self.detect_model()

        if model == 'gs1900':
            content = self.get_page(512)  # System Information cmd
        elif model == 'gs1915':
            content = self.get_page('/rpsysinfo.html')  # lowercase for GS1915
        else:  # gs1920
            content = self.get_page('/rpSysinfo.html')

        return self._parse_system_info(content, model)

    def _parse_system_info(self, content, model):
        """Parse system information from HTML content."""
        info = {
            'model': model,
            'hostname': '',
            'firmware': '',
            'mac_address': '',
        }

        if model == 'gs1900':
            # Parse GS1900 format
            name_match = re.search(r'name="system_name"[^>]*value="([^"]*)"', content)
            if name_match:
                info['hostname'] = name_match.group(1)
        else:
            # Parse GS1915/GS1920 format
            name_match = re.search(r'System Name[^<]*</td>\s*<td[^>]*>([^<]+)', content)
            if name_match:
                info['hostname'] = name_match.group(1).strip()

            model_match = re.search(r'Product Model[^<]*</td>\s*<td[^>]*>([^<]+)', content)
            if model_match:
                info['model'] = model_match.group(1).strip()

            fw_match = re.search(r'F/W Version[^<]*</td>\s*<td[^>]*>([^<]+)', content)
            if fw_match:
                info['firmware'] = fw_match.group(1).strip()

            mac_match = re.search(r'Ethernet Address[^<]*</td>\s*<td[^>]*>([^<]+)', content)
            if mac_match:
                info['mac_address'] = mac_match.group(1).strip()

        return info

    def get_ports_info(self):
        """Get port information from the switch."""
        model = self.detect_model()

        if model == 'gs1900':
            content = self.get_page('/cgi-bin/dispatcher.cgi?cmd=768')
        elif model == 'gs1915':
            content = self.get_page('/rpport.html')  # lowercase for GS1915
        else:  # gs1920
            content = self.get_page('/rpPort.html')

        return self._parse_ports_info(content, model)

    def _parse_ports_info(self, content, model):
        """Parse port information from HTML content."""
        ports = {}

        if model == 'gs1900':
            # GS1900 uses cmd=768 with table format
            # Pattern: checkbox value, port num, name, state, link, speed, duplex, flowctrl
            pattern = (
                r'<input type="checkbox" name="port" value="(\d+)"'
                r'.*?<td class="font-4" ><div align=center>\s*\d+\s*</div></td>\s*'  # Port num
                r'<td class="font-4" ><div align=center>\s*([^<]*?)\s*</div></td>\s*'  # Name
                r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'  # State
                r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'  # Link Status
                r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'  # Speed
                r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'  # Duplex
                r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>'      # FlowCtrl
            )
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for port, name, state, link, speed, duplex, flowctrl in matches:
                ports[port] = {
                    'name': name.strip(),
                    'enabled': state.lower() == 'enable',
                    'link_status': link.lower(),
                    'speed': speed.lower(),
                    'duplex': duplex.lower(),
                    'flow_control': flowctrl.lower() == 'enable',
                }
        elif model == 'gs1915':
            # GS1915 uses rpport.html with different field names
            # Port names: rpport_IptPortName?{port}
            name_matches = re.findall(
                r'rpport_IptPortName\?(\d+)"[^>]*VALUE="([^"]*)"',
                content, re.IGNORECASE
            )
            for port_id, name in name_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['name'] = name

            # Port active: rpport_ChkPortActive with VALUE="?{port}" and CHECKED
            active_matches = re.findall(
                r'rpport_ChkPortActive[^>]*VALUE="\?(\d+)"([^>]*)',
                content, re.IGNORECASE
            )
            for port_id, attrs in active_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['enabled'] = 'CHECKED' in attrs.upper()

            # Speed: rpport_SltSpeed?{port} with SELECTED option
            speed_pattern = r'rpport_SltSpeed\?(\d+)"[^>]*>.*?<OPTION[^>]*SELECTED[^>]*>([^<]+)'
            speed_matches = re.findall(speed_pattern, content, re.IGNORECASE | re.DOTALL)
            for port_id, speed_name in speed_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['speed'] = speed_name.strip().lower()
        else:
            # GS1920 format - parse form inputs
            # Find port names - VALUE attribute is case-insensitive
            name_matches = re.findall(
                r'rpPort_Ipt_PortName\?(\d+)"[^>]*VALUE="([^"]*)"',
                content, re.IGNORECASE
            )
            for port_id, name in name_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['name'] = name

            # Find port states (checkboxes) - checked attribute
            active_matches = re.findall(
                r'rpPort_Chk_PortActive[^>]*value="\?(\d+)"[^>]*checked',
                content, re.IGNORECASE
            )
            for port_id in active_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['enabled'] = True

            # Find speed settings - look for SELECTED option
            speed_pattern = r'rpPort_Slt_Speed\?(\d+)"[^>]*>.*?<OPTION\s+VALUE=(\w+)\s+SELECTED>([^<]+)'
            speed_matches = re.findall(speed_pattern, content, re.IGNORECASE | re.DOTALL)
            for port_id, speed_val, speed_name in speed_matches:
                if port_id not in ports:
                    ports[port_id] = {'enabled': False, 'name': '', 'speed': 'auto'}
                ports[port_id]['speed'] = speed_name.strip().lower()

        return ports

    def get_vlans_info(self):
        """Get VLAN information from the switch.

        GS1920: Uses rpVlantag.html for VLAN list, rpVlanport.html for port settings
        GS1915: Uses rpvlantag.html for VLAN list (lowercase), rpvlanport.html for port settings
        GS1900: Uses different format
        """
        model = self.detect_model()

        if model == 'gs1900':
            # GS1900 uses cmd=1283 for the AJAX VLAN list
            content = self.get_page('/cgi-bin/dispatcher.cgi?cmd=1283&pageindex=1')
            vlans = self._parse_vlans_info_gs1900(content)
            # Get port PVID settings to determine untagged port membership
            port_content = self.get_page('/cgi-bin/dispatcher.cgi?cmd=1290')
            port_settings = self._parse_port_settings_gs1900(port_content)
            # Build untagged port membership from PVID assignments
            for port_id, settings in port_settings.items():
                pvid = str(settings.get('pvid', 1))
                if pvid in vlans:
                    if port_id not in vlans[pvid]['untagged_ports']:
                        vlans[pvid]['untagged_ports'].append(port_id)
            # Sort port lists
            for vid in vlans:
                vlans[vid]['untagged_ports'] = sorted(
                    vlans[vid]['untagged_ports'],
                    key=lambda x: int(x) if x.isdigit() else 0
                )
            return vlans
        elif model == 'gs1915':
            # GS1915 uses rpvlantag.html (lowercase) for VLAN list
            # The ?1,1 parameter shows the add form with the VLAN list table
            tag_content = self.get_page('/rpvlantag.html?1,1')
            port_content = self.get_page('/rpvlanport.html')
            vlans = self._parse_vlans_from_tag_page_gs1915(tag_content)
            # Supplement with PVID data
            port_settings = self._parse_vlan_port_settings(port_content)
        else:  # gs1920
            tag_content = self.get_page('/rpVlantag.html')  # Tag page has ALL VLANs
            port_content = self.get_page('/rpVlanport.html')  # Port page has PVID info
            vlans = self._parse_vlans_from_tag_page(tag_content, model)
            port_settings = self._parse_vlan_port_settings(port_content)

        # Build untagged port membership from PVID assignments
        for port_id, settings in port_settings.items():
            pvid = str(settings.get('pvid', 1))
            if pvid in vlans:
                if port_id not in vlans[pvid]['untagged_ports']:
                    vlans[pvid]['untagged_ports'].append(port_id)

        # Sort port lists for consistent output
        for vid in vlans:
            vlans[vid]['untagged_ports'] = sorted(
                vlans[vid]['untagged_ports'],
                key=lambda x: int(x) if x.isdigit() else 0
            )

        return vlans

    def _parse_vlans_from_tag_page(self, content, model):
        """Parse VLAN information from rpVlantag.html page.

        The tag page shows ALL VLANs with: checkbox, VID, Active (ON/OFF), Name
        HTML structure (with tabs/newlines):
          <INPUT TYPE="CHECKBOX" NAME="rpVlantag_Chk_TabDel" VALUE="?1">
            <label>&nbsp;</label>
          </td>
          <td>1   </td>
          <td><span class="status-on">ON</span></td>
          <td style="text-align:left" class="word-break">CORE</td>
        """
        vlans = {}

        # Pattern to match VLAN rows - find checkbox name, then VID and Name
        # The checkbox VALUE="?N" is followed by VID in next <td>, status span, then name
        row_pattern = (
            r'NAME="rpVlantag_Chk_TabDel"\s+VALUE="\?\d+"'  # Checkbox with index
            r'.*?</td>\s*'                                   # Close checkbox td
            r'<td[^>]*>(\d+)\s*</td>\s*'                    # VID
            r'<td[^>]*>.*?</td>\s*'                         # Active status (ON/OFF span)
            r'<td[^>]*>\s*(\S[^<]*?)\s*</td>'               # Name (non-empty, trimmed)
        )
        matches = re.findall(row_pattern, content, re.IGNORECASE | re.DOTALL)
        for vid, name in matches:
            vlans[vid.strip()] = {
                'name': name.strip(),
                'tagged_ports': [],
                'untagged_ports': [],
            }

        return vlans

    def _parse_vlans_info_gs1900(self, content):
        """Parse VLAN information for GS1900 series.

        GS1900 uses cmd=1283 for VLAN list with AJAX.
        HTML structure:
          <td class="font-4" ><div align=center>1</div></td>
          <td class="font-4" ><div align=center>default</div></td>
          <td class="font-4" ><div align=center>Default</div></td>
        """
        vlans = {}

        # GS1900 VLAN list pattern: VID, Name, Type (Default/Static)
        pattern = (
            r'<td class="font-4" ><div align=center>\s*(\d+)\s*</div></td>\s*'
            r'<td class="font-4" ><div align=center>\s*([^<]*?)\s*</div></td>\s*'
            r'<td class="font-4" ><div align=center>\s*(Default|Static)\s*</div></td>'
        )
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for vid, name, vtype in matches:
            vlans[vid.strip()] = {
                'name': name.strip(),
                'tagged_ports': [],
                'untagged_ports': [],
                'active': True,  # GS1900 doesn't have active/inactive concept
            }

        return vlans

    def _parse_port_settings_gs1900(self, content):
        """Parse port settings from GS1900 cmd=1290.

        HTML structure:
          <input type="checkbox" name="port" value="1">
          ...
          <td class="font-4" ><div align=center>1</div></td>  (Port)
          <td class="font-4" ><div align=center>119</div></td>  (PVID)
          <td class="font-4" ><div align=center>ALL</div></td>  (AcceptFrame)
          <td class="font-4" ><div align=center>Disable</div></td>  (IngressCheck)
          <td class="font-4" ><div align=center>Disable</div></td>  (VLANTrunk)
        """
        ports = {}

        # Pattern to extract port settings
        pattern = (
            r'<input type="checkbox" name="port" value="(\d+)"'
            r'.*?<td class="font-4" ><div align=center>\s*\d+\s*</div></td>\s*'  # Port num
            r'<td class="font-4" ><div align=center>\s*(\d+)\s*</div></td>\s*'   # PVID
            r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'   # AcceptFrame
            r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>\s*'   # IngressCheck
            r'<td class="font-4" ><div align=center>\s*(\w+)\s*</div></td>'      # VLANTrunk
        )
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for port, pvid, accept_frame, ingress, trunk in matches:
            ports[port] = {
                'pvid': int(pvid),
                'accept_frame_type': accept_frame,
                'ingress_filtering': ingress.lower() == 'enable',
                'vlan_trunking': trunk.lower() == 'enable',
            }

        return ports

    def _parse_vlans_info_gs1915(self, content):
        """Parse VLAN information from GS1915 rpvlanstatusStatistics.html.

        Each row has: index, VID, Name, Untagged ports, Tagged ports, Uptime, Type
        Example: <a href='US/121/rpvlanstatusStatisticsDetail.html'>8</a> 121 VOV 1-2,21-24
        """
        vlans = {}

        # Pattern to extract VLAN data from the status page rows
        pattern = (
            r"<a href='US/(\d+)/rpvlanstatusStatisticsDetail\.html'[^>]*>\s*\d+\s*</a>"
            r".*?<div align=center>\s*(\d+)\s*</div>"  # VID (duplicated in URL and column)
            r".*?<div align=center>\s*([^<]*?)\s*</div>"  # Name
            r".*?<div align=center>\s*([^<]*?)\s*</div>"  # Untagged ports
            r".*?<div align=center>\s*([^<]*?)\s*</div>"  # Tagged ports
        )
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for vlan_id, vid2, name, untagged, tagged in matches:
            # Use the VID from the URL (vlan_id)
            vid = vlan_id.strip()
            vlans[vid] = {
                'name': name.strip(),
                'tagged_ports': self._parse_port_range(tagged.strip()),
                'untagged_ports': self._parse_port_range(untagged.strip()),
            }

        return vlans

    def _parse_vlans_from_tag_page_gs1915(self, content):
        """Parse VLAN information from GS1915 rpvlantag.html page.

        The tag page shows ALL VLANs with: VID link, Active (Yes/No), Name
        HTML structure:
          <a href="javascript:GetIndexID(121);">121</a>
          ...
          <div align=center>Yes</div>
          ...
          <div align=center>VOV</div>
        """
        vlans = {}

        # Pattern to match VLAN rows - find GetIndexID(VID) followed by Active and Name
        row_pattern = (
            r'GetIndexID\((\d+)\)[^<]*</a>'  # VID from JavaScript link
            r'.*?<div align=center>\s*(Yes|No)\s*</div>'  # Active status
            r'.*?<div align=center>\s*([^<]*?)\s*</div>'  # Name
        )
        matches = re.findall(row_pattern, content, re.IGNORECASE | re.DOTALL)
        for vid, active, name in matches:
            vlans[vid.strip()] = {
                'name': name.strip(),
                'tagged_ports': [],
                'untagged_ports': [],
                'active': active.lower() == 'yes',
            }

        return vlans

    def get_vlan_port_settings(self):
        """Get VLAN port settings including PVID from rpVlanport.html."""
        model = self.detect_model()

        if model == 'gs1900':
            content = self.get_page('/cgi-bin/dispatcher.cgi?cmd=1290')
            return self._parse_port_settings_gs1900(content)
        elif model == 'gs1915':
            content = self.get_page('/rpvlanport.html')
        else:  # gs1920
            content = self.get_page('/rpVlanport.html')

        return self._parse_vlan_port_settings(content)

    def _parse_vlan_port_settings(self, content):
        """Parse VLAN port settings from rpVlanport.html.

        Extracts PVID, Ingress filtering, Acceptable Frame Type, VLAN Trunking, Port Isolation
        Supports both GS1920 (rpVlanport_Ipt_PVID) and GS1915 (rpvlanport_IptPVID) formats.
        """
        ports = {}

        # Parse PVID values - try both formats
        # GS1920: rpVlanport_Ipt_PVID?1  GS1915: rpvlanport_IptPVID?1
        pvid_patterns = [
            r'rpVlanport_Ipt_PVID\?(\d+)[^>]*VALUE="(\d+)"',
            r'rpvlanport_IptPVID\?(\d+)[^>]*VALUE="(\d+)"',
        ]
        for pvid_pattern in pvid_patterns:
            pvid_matches = re.findall(pvid_pattern, content, re.IGNORECASE)
            for port_id, pvid in pvid_matches:
                if port_id not in ports:
                    ports[port_id] = {}
                ports[port_id]['pvid'] = int(pvid)

        # Parse Ingress Filtering: checked means enabled
        # GS1920: rpVlanport_Chk_Ingress  GS1915: rpvlanport_ChkIngress
        ingress_patterns = [
            r'rpVlanport_Chk_Ingress[^>]*VALUE="\?(\d+)"([^>]*)',
            r'rpvlanport_ChkIngress[^>]*VALUE="\?(\d+)"([^>]*)',
        ]
        for ingress_pattern in ingress_patterns:
            ingress_matches = re.findall(ingress_pattern, content, re.IGNORECASE)
            for port_id, attrs in ingress_matches:
                if port_id not in ports:
                    ports[port_id] = {}
                ports[port_id]['ingress_filtering'] = 'CHECKED' in attrs.upper()

        # Parse VLAN Trunking: checked means enabled
        # GS1920: rpVlanport_Chk_VLANTrunking  GS1915: rpvlanport_ChkVLANTrunking
        trunk_patterns = [
            r'rpVlanport_Chk_VLANTrunking[^>]*VALUE="\?(\d+)"([^>]*)',
            r'rpvlanport_ChkVLANTrunking[^>]*VALUE="\?(\d+)"([^>]*)',
        ]
        for trunk_pattern in trunk_patterns:
            trunk_matches = re.findall(trunk_pattern, content, re.IGNORECASE)
            for port_id, attrs in trunk_matches:
                if port_id not in ports:
                    ports[port_id] = {}
                ports[port_id]['vlan_trunking'] = 'CHECKED' in attrs.upper()

        # Parse Acceptable Frame Type from select
        # Options: All Frames (0), Tagged Only (1), Untagged Only (2)
        # GS1920: rpVlanport_Slt_AcceptableFrame  GS1915: rpvlanport_SltAcceptableFrame
        frame_patterns = [
            r'rpVlanport_Slt_AcceptableFrame\?(\d+)[^>]*>.*?<OPTION[^>]*VALUE="?(\d+)"?[^>]*SELECTED',
            r'rpvlanport_SltAcceptableFrame\?(\d+)[^>]*>.*?<OPTION[^>]*VALUE="?(\d+)"?[^>]*SELECTED',
        ]
        frame_types = {0: 'all', 1: 'tagged_only', 2: 'untagged_only'}
        for frame_pattern in frame_patterns:
            frame_matches = re.findall(frame_pattern, content, re.IGNORECASE | re.DOTALL)
            for port_id, frame_type in frame_matches:
                if port_id not in ports:
                    ports[port_id] = {}
                ports[port_id]['acceptable_frame_type'] = frame_types.get(int(frame_type), 'all')

        return ports

    def _parse_port_range(self, port_str):
        """Parse port range string like '1-4,6,8-10' into list of port numbers."""
        if not port_str:
            return []
        ports = []
        for part in port_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = part.split('-')
                    ports.extend([str(p) for p in range(int(start), int(end) + 1)])
                except ValueError:
                    continue
            elif part.isdigit():
                ports.append(part)
        return ports

    def _parse_form_checkboxes(self, content, name_pattern):
        """Parse checked checkboxes from HTML form.

        Args:
            content: HTML content
            name_pattern: Regex pattern to match NAME attribute

        Returns:
            List of values that are checked
        """
        checked = []
        pattern = r'<INPUT[^>]*NAME="%s"[^>]*VALUE="([^"]*)"[^>]*>' % name_pattern
        for match in re.finditer(pattern, content, re.IGNORECASE):
            if 'CHECKED' in match.group(0).upper():
                checked.append(match.group(1))
        return checked

    def _parse_form_inputs(self, content, name_pattern):
        """Parse text input values from HTML form.

        Args:
            content: HTML content
            name_pattern: Regex pattern to match NAME attribute

        Returns:
            Dict of {field_name: value}
        """
        inputs = {}
        pattern = r'<INPUT[^>]*NAME="(%s)"[^>]*VALUE="([^"]*)"' % name_pattern
        for match in re.finditer(pattern, content, re.IGNORECASE):
            inputs[match.group(1)] = match.group(2)
        return inputs

    def _parse_form_selects(self, content, name_pattern):
        """Parse select dropdown values from HTML form.

        Args:
            content: HTML content
            name_pattern: Regex pattern to match NAME attribute

        Returns:
            Dict of {field_name: selected_value}
        """
        selects = {}
        # Match SELECT with SELECTED OPTION
        pattern = r'<SELECT[^>]*NAME="(%s)"[^>]*>.*?<OPTION[^>]*VALUE="([^"]*)"[^>]*SELECTED' % name_pattern
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            selects[match.group(1)] = match.group(2)
        # Also try SELECTED before VALUE
        pattern2 = r'<SELECT[^>]*NAME="(%s)"[^>]*>.*?<OPTION[^>]*SELECTED[^>]*VALUE="([^"]*)"' % name_pattern
        for match in re.finditer(pattern2, content, re.IGNORECASE | re.DOTALL):
            if match.group(1) not in selects:
                selects[match.group(1)] = match.group(2)
        return selects

    def get_vlan_tag_page(self):
        """Get the VLAN tag configuration page (rpVlantag.html)."""
        model = self.detect_model()
        if model == 'gs1900':
            return self.get_page(1282)
        elif model == 'gs1915':
            return self.get_page('/rpvlantag.html')
        else:  # gs1920
            return self.get_page('/rpVlantag.html')

    def get_vlan_index(self, vlan_id):
        """Get the table index for a VLAN ID.

        Returns the checkbox value (e.g., '1,13' for slot 1, index 13) or None if VLAN doesn't exist.
        For GS1915, returns 'slot,index' format used by rpvlantag_ChkDel.
        For GS1920, returns just the index number.
        """
        model = self.detect_model()

        if model == 'gs1915':
            # GS1915: Parse from rpvlantag.html to find the ChkDel value for this VLAN
            # The checkbox VALUE is like "?slot,index" and we need to find which row has our VLAN ID
            content = self.get_page('/rpvlantag.html?1,1')
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL | re.IGNORECASE)
            for row in rows:
                chk_match = re.search(r'rpvlantag_ChkDel[^>]*VALUE="\?([^"]+)"', row, re.IGNORECASE)
                vid_match = re.search(r'GetIndexID\((\d+)\)', row)
                if chk_match and vid_match and vid_match.group(1) == str(vlan_id):
                    return chk_match.group(1)  # Returns 'slot,index' format
            return None
        else:
            # GS1920: Parse tbody rows from rpVlantag.html
            content = self.get_vlan_tag_page()
            tbody_match = re.search(r'<tbody>(.*?)</tbody>', content, re.DOTALL)
            if tbody_match:
                rows = re.findall(r'<tr>(.*?)</tr>', tbody_match.group(1), re.DOTALL)
                for row in rows:
                    chk = re.search(r'VALUE="\?(\d+)"', row)
                    vid = re.search(r'</td>\s*<td>(\d+)\s*</td>', row)
                    if chk and vid and vid.group(1) == str(vlan_id):
                        return chk.group(1)
            return None

    def create_vlan(self, config):
        """Create or update a VLAN on the switch.

        Args:
            config: Dict with keys:
                - vlan_id: VLAN ID (1-4094)
                - vlan_name: VLAN name (optional)
                - tagged_ports: List of port numbers for tagged membership
                - untagged_ports: List of port numbers for untagged membership
                - num_ports: Total number of ports on the switch (default 28)

        Returns:
            Dict with 'success' and 'msg' keys
        """
        vlan_id = config.get('vlan_id')
        vlan_name = config.get('vlan_name')
        tagged_ports = config.get('tagged_ports', [])
        untagged_ports = config.get('untagged_ports', [])
        num_ports = config.get('num_ports', 28)

        model = self.detect_model()
        if model == 'gs1900':
            success, msg = self._create_vlan_gs1900(vlan_id, vlan_name, tagged_ports, untagged_ports)
        elif model == 'gs1915':
            success, msg = self._create_vlan_gs1915(vlan_id, vlan_name, tagged_ports, untagged_ports, num_ports)
        else:  # gs1920
            success, msg = self._create_vlan_gs1920(vlan_id, vlan_name, tagged_ports, untagged_ports, num_ports)

        return {'success': success, 'msg': msg}

    def _create_vlan_gs1915(self, vlan_id, name, tagged_ports, untagged_ports, num_ports):
        """Create VLAN on GS1915 series."""
        tagged_ports = [str(p) for p in (tagged_ports or [])]
        untagged_ports = [str(p) for p in (untagged_ports or [])]

        # Build the VLAN creation form as list of tuples
        form_data = [
            ('rpvlantag_ChkActive', 'on'),
            ('rpvlantag_IptName', name or ('VLAN%s' % vlan_id)),
            ('rpvlantag_IptGroupID', str(vlan_id)),
            ('rpvlantag_HidBtnID', '1'),  # 1=Add
            ('rpvlantag_HidEditMode', '0'),
            ('rpvlantag_HidSelectedIndex', '0'),
            ('rpvlantag_HidBtnNum', '0'),
            ('rpvlantag_HidOldSlot', '0'),
        ]

        # Set port membership for each port
        # RpgControl: 0=Normal(not member), 1=Fixed(member), 2=Forbidden
        # ChkTagging: checked=TX tagged, unchecked=TX untagged
        for port in range(1, num_ports + 1):
            port_str = str(port)
            if port_str in tagged_ports:
                form_data.append(('rpvlantag_RpgControl?%d' % port, '1'))
                form_data.append(('rpvlantag_ChkTagging', '?%d' % port))
            elif port_str in untagged_ports:
                form_data.append(('rpvlantag_RpgControl?%d' % port, '1'))
            else:
                form_data.append(('rpvlantag_RpgControl?%d' % port, '0'))

        code, response = self.post_form('/Forms/rpvlantag_1', form_data)
        if code == 200 and 'Error' not in response:
            return True, 'VLAN %s created' % vlan_id
        return False, 'Failed to create VLAN %s: HTTP %d' % (vlan_id, code)

    def _create_vlan_gs1920(self, vlan_id, name, tagged_ports, untagged_ports, num_ports):
        """Create VLAN on GS1920 series."""
        tagged_ports = [str(p) for p in (tagged_ports or [])]
        untagged_ports = [str(p) for p in (untagged_ports or [])]

        # First, open the add dialog (NumID=2)
        data = {
            'rpVlantag_HidBtn_IndexID': '0',
            'rpVlantag_HidBtn_NumID': '2',
        }
        self.post_form('/Forms/rpVlantag_1', data)

        # Build the VLAN creation form as list of tuples
        form_data = [
            ('rpVlantag_Toggle_Chk_Active', 'on'),
            ('rpVlantag_Toggle_Ipt_Name', name or ('VLAN%s' % vlan_id)),
            ('rpVlantag_Toggle_Ipt_VlanGroupID', str(vlan_id)),
            ('rpVlantag_HidBtn_IndexID', '0'),
            ('rpVlantag_HidBtn_NumID', '5'),  # Apply/Create
        ]

        # Set port membership for each port
        # Rdo_Control: 0=Normal(not member), 1=Fixed(member), 2=Forbidden
        # Chk_Tagging: checked=TX tagged, unchecked=TX untagged
        for port in range(1, num_ports + 1):
            port_str = str(port)
            if port_str in tagged_ports:
                form_data.append(('rpVlantag_Toggle_Rdo_Control?%d' % port, '1'))
                form_data.append(('rpVlantag_Toggle_Chk_Tagging', '?%d' % port))
            elif port_str in untagged_ports:
                form_data.append(('rpVlantag_Toggle_Rdo_Control?%d' % port, '1'))
            else:
                form_data.append(('rpVlantag_Toggle_Rdo_Control?%d' % port, '0'))

        code, response = self.post_form('/Forms/rpVlantag_1', form_data)
        if code == 200 and 'Error' not in response:
            return True, 'VLAN %s created' % vlan_id
        return False, 'Failed to create VLAN %s: HTTP %d' % (vlan_id, code)

    def _create_vlan_gs1900(self, vlan_id, name, tagged_ports, untagged_ports):
        """Create VLAN on GS1900 series.

        GS1900 uses cmd=1284 for the add form and cmd=1285 for submit.
        Form fields: vlanlist, name, XSSID
        """
        # Get XSSID token from the add form (cmd=1284)
        xssid = self._get_gs1900_xssid(1284)
        if not xssid:
            return False, 'Failed to get XSSID token for VLAN creation'

        # Build form data
        data = {
            'cmd': 1285,  # Submit command
            'XSSID': xssid,
            'vlanlist': str(vlan_id),
            'name': name or ('VLAN%s' % vlan_id),
            'vlanAction': '0',  # 0=Add
        }

        code, response = self.post_form(1285, data)
        if code == 200:
            return True, 'VLAN %s created' % vlan_id
        return False, 'Failed to create VLAN %s: HTTP %d' % (vlan_id, code)

    def delete_vlan(self, vlan_id):
        """Delete a VLAN from the switch.

        Args:
            vlan_id: VLAN ID to delete

        Returns:
            Tuple of (success, message)
        """
        model = self.detect_model()
        if model == 'gs1900':
            return self._delete_vlan_gs1900(vlan_id)
        elif model == 'gs1915':
            return self._delete_vlan_gs1915(vlan_id)
        else:  # gs1920
            return self._delete_vlan_gs1920(vlan_id)

    def _delete_vlan_gs1915(self, vlan_id):
        """Delete VLAN on GS1915 series."""
        # Find the VLAN's checkbox value (format: 'slot,index')
        idx = self.get_vlan_index(vlan_id)
        if idx is None:
            return True, 'VLAN %s does not exist' % vlan_id

        # GS1915 delete: HidBtnID=2, checkbox name is rpvlantag_ChkDel
        # The checkbox value format is '?slot,index' (e.g., '?1,13')
        form_data = [
            ('rpvlantag_ChkDel', '?%s' % idx),
            ('rpvlantag_HidBtnID', '2'),  # 2=Delete
            ('rpvlantag_HidEditMode', '0'),
            ('rpvlantag_HidSelectedIndex', '0'),
            ('rpvlantag_HidBtnNum', '0'),
            ('rpvlantag_HidOldSlot', '0'),
        ]
        code, response = self.post_form('/Forms/rpvlantag_1', form_data)

        # Verify deletion
        if self.get_vlan_index(vlan_id) is None:
            return True, 'VLAN %s deleted' % vlan_id
        return False, 'Failed to delete VLAN %s' % vlan_id

    def _delete_vlan_gs1920(self, vlan_id):
        """Delete VLAN on GS1920 series."""
        # Find the VLAN's table index
        idx = self.get_vlan_index(vlan_id)
        if idx is None:
            return True, 'VLAN %s does not exist' % vlan_id

        # Step 1: Initiate delete (NumID=4)
        data = {
            'rpVlantag_Chk_TabDel': '?%s' % idx,
            'rpVlantag_HidBtn_IndexID': idx,
            'rpVlantag_HidBtn_NumID': '4',
        }
        self.post_form('/Forms/rpVlantag_1', data)

        # Step 2: Confirm delete (NumID=7)
        data = {
            'rpVlantag_Chk_TabDel': '?%s' % idx,
            'rpVlantag_HidBtn_IndexID': idx,
            'rpVlantag_HidBtn_NumID': '7',
        }
        code, response = self.post_form('/Forms/rpVlantag_1', data)

        # Verify deletion
        if self.get_vlan_index(vlan_id) is None:
            return True, 'VLAN %s deleted' % vlan_id
        return False, 'Failed to delete VLAN %s' % vlan_id

    def _delete_vlan_gs1900(self, vlan_id):
        """Delete VLAN on GS1900 series."""
        data = {
            'cmd': 1282,
            'vid': str(vlan_id),
            'action': 'delete',
        }
        code, response = self.post_form(1282, data)
        if code == 200:
            return True, 'VLAN %s deleted' % vlan_id
        return False, 'Failed to delete VLAN %s' % vlan_id

    def set_port_pvid(self, port_id, pvid, num_ports=28, vlan_trunking=None,
                       ingress_filtering=None, acceptable_frame_type=None):
        """Set the PVID (native VLAN) and related settings for a port.

        Args:
            port_id: Port number
            pvid: VLAN ID to set as PVID
            num_ports: Total number of ports on the switch
            vlan_trunking: Enable VLAN trunking (True/False/None=preserve)
            ingress_filtering: Enable ingress filtering (True/False/None=preserve)
            acceptable_frame_type: 'all', 'tagged', or 'untagged' (None=preserve)

        Returns:
            Tuple of (success, message)
        """
        model = self.detect_model()
        if model == 'gs1900':
            return self._set_port_pvid_gs1900(
                port_id, pvid, vlan_trunking,
                ingress_filtering, acceptable_frame_type
            )
        elif model == 'gs1915':
            return self._set_port_pvid_gs1915(
                port_id, pvid, num_ports, vlan_trunking,
                ingress_filtering, acceptable_frame_type
            )
        else:  # gs1920
            return self._set_port_pvid_gs1920(
                port_id, pvid, num_ports, vlan_trunking,
                ingress_filtering, acceptable_frame_type
            )

    def _set_port_pvid_gs1915(self, port_id, pvid, num_ports, vlan_trunking=None,
                               ingress_filtering=None, acceptable_frame_type=None):
        """Set port PVID and VLAN settings on GS1915 series."""
        # Get current port VLAN settings
        content = self.get_page('/rpvlanport.html')

        # Parse current settings for all ports
        current_settings = self._parse_vlan_port_settings(content)

        # Build form data - GS1915 uses lowercase field names
        form_data = [('rpvlanport_HidBtnNum', '1')]  # Apply

        for port in range(1, num_ports + 1):
            port_str = str(port)
            current = current_settings.get(port_str, {})

            # Set PVID - GS1915: rpvlanport_IptPVID?{port}
            if port == int(port_id):
                form_data.append(('rpvlanport_IptPVID?%d' % port, str(pvid)))
            else:
                current_pvid = current.get('pvid', 1)
                form_data.append(('rpvlanport_IptPVID?%d' % port, str(current_pvid)))

            # VLAN Trunking checkbox - GS1915: rpvlanport_ChkVLANTrunking
            if port == int(port_id) and vlan_trunking is not None:
                set_trunking = vlan_trunking
            else:
                set_trunking = current.get('vlan_trunking', False)
            if set_trunking:
                form_data.append(('rpvlanport_ChkVLANTrunking', '?%d' % port))

        code, response = self.post_form('/Forms/rpvlanport_1', form_data)
        if code == 200 and 'Error' not in response:
            return True, 'Port %s PVID set to %s' % (port_id, pvid)
        return False, 'Failed to set port %s PVID' % port_id

    def _set_port_pvid_gs1920(self, port_id, pvid, num_ports, vlan_trunking=None,
                               ingress_filtering=None, acceptable_frame_type=None):
        """Set port PVID and VLAN settings on GS1920 series."""
        # Get current port VLAN settings
        content = self.get_page('/rpVlanport.html')

        # Parse current settings for all ports
        current_settings = self._parse_vlan_port_settings(content)

        # Build form data - checkboxes use list of tuples
        form_data = [('rpVlanport_HidBtn_NumID', '1')]  # Apply

        for port in range(1, num_ports + 1):
            port_str = str(port)
            current = current_settings.get(port_str, {})

            # Set PVID
            if port == int(port_id):
                form_data.append(('rpVlanport_Ipt_PVID?%d' % port, str(pvid)))
            else:
                current_pvid = current.get('pvid', 1)
                form_data.append(('rpVlanport_Ipt_PVID?%d' % port, str(current_pvid)))

            # Acceptable frame type: 00000000=all, 00000001=tagged, 00000002=untagged
            if port == int(port_id) and acceptable_frame_type is not None:
                aft_map = {'all': '00000000', 'tagged': '00000001', 'untagged': '00000002'}
                aft_value = aft_map.get(acceptable_frame_type, '00000000')
            else:
                # Preserve current setting
                current_aft = current.get('acceptable_frame_type', 'all')
                aft_map = {'all': '00000000', 'tagged': '00000001', 'untagged': '00000002'}
                aft_value = aft_map.get(current_aft, '00000000')
            form_data.append(('rpVlanport_Slt_AcceptableFrame?%d' % port, aft_value))

            # Ingress filtering checkbox
            if port == int(port_id) and ingress_filtering is not None:
                set_ingress = ingress_filtering
            else:
                set_ingress = current.get('ingress_filtering', False)
            if set_ingress:
                form_data.append(('rpVlanport_Chk_Ingress', '?%d' % port))

            # VLAN Trunking checkbox
            if port == int(port_id) and vlan_trunking is not None:
                set_trunking = vlan_trunking
            else:
                set_trunking = current.get('vlan_trunking', False)
            if set_trunking:
                form_data.append(('rpVlanport_Chk_VLANTrunking', '?%d' % port))

        code, response = self.post_form('/Forms/rpVlanport_1', form_data)
        if code == 200 and 'Error' not in response:
            return True, 'Port %s PVID set to %s' % (port_id, pvid)
        return False, 'Failed to set port %s PVID' % port_id

    def _set_port_pvid_gs1900(self, port_id, pvid, vlan_trunking=None,
                               ingress_filtering=None, acceptable_frame_type=None):
        """Set port PVID on GS1900 series.

        GS1900 uses cmd=1291 for the edit form and cmd=1292 for submit.
        Form fields: portlist, pvid, frametype, vlan_igrfilter, vlan_trunk, XSSID
        """
        # Get XSSID token from the edit form (cmd=1291)
        xssid = self._get_gs1900_xssid(1291)
        if not xssid:
            return False, 'Failed to get XSSID token for PVID setting'

        # Map acceptable_frame_type to frametype value
        frametype_map = {'all': '0', 'tagged': '1', 'untagged': '2'}
        frametype = frametype_map.get(acceptable_frame_type, '0') if acceptable_frame_type else '0'

        # Build form data
        data = {
            'cmd': 1292,  # Submit command
            'XSSID': xssid,
            'portlist': str(port_id),
            'pvid': str(pvid),
            'frametype': frametype,
            'vlan_igrfilter': '1' if ingress_filtering else '0',
            'vlan_trunk': '1' if vlan_trunking else '0',
        }

        code, response = self.post_form(1292, data)
        if code == 200:
            return True, 'Port %s PVID set to %s' % (port_id, pvid)
        return False, 'Failed to set port %s PVID: HTTP %d' % (port_id, code)

    def configure_port(self, port_id, config):
        """Configure a port on the switch."""
        model = self.detect_model()

        if model == 'gs1900':
            return self._configure_port_gs1900(port_id, config)
        elif model == 'gs1915':
            return self._configure_port_gs1915(port_id, config)
        else:  # gs1920
            return self._configure_port_gs1920(port_id, config)

    def _configure_port_gs1915(self, port_id, config):
        """Configure port on GS1915 using read-modify-write pattern."""
        # STEP 1: READ current port page
        content = self.get_page('/rpport.html')

        # Parse all currently enabled ports (checkboxes)
        # GS1915 uses rpport_ChkPortActive with VALUE="?{port}"
        enabled_ports = set()
        for match in re.finditer(
            r'<INPUT[^>]*NAME="rpport_ChkPortActive"[^>]*VALUE="\?(\d+)"[^>]*>',
            content, re.IGNORECASE
        ):
            if 'CHECKED' in match.group(0).upper():
                enabled_ports.add(match.group(1))

        # Parse all port names - GS1915: rpport_IptPortName?{port}
        port_names = self._parse_form_inputs(content, r'rpport_IptPortName\?\d+')

        # Parse all port speeds - GS1915: rpport_SltSpeed?{port}
        port_speeds = self._parse_form_selects(content, r'rpport_SltSpeed\?\d+')

        # STEP 2: MODIFY - apply requested changes
        port_id_str = str(port_id)

        if config.get('enabled') is not None:
            if config['enabled']:
                enabled_ports.add(port_id_str)
            else:
                enabled_ports.discard(port_id_str)

        if config.get('name') is not None:
            port_names['rpport_IptPortName?%s' % port_id_str] = config['name']

        if config.get('speed') is not None:
            speed_map = {
                'auto': '00000000',
                '10m-half': '00000006',
                '10m-full': '00000007',
                '100m-half': '00000004',
                '100m-full': '00000005',
                '1g-full': '00000003',
            }
            port_speeds['rpport_SltSpeed?%s' % port_id_str] = speed_map.get(
                config['speed'], '00000000'
            )

        # STEP 3: WRITE - build form data with ALL current state
        form_data = []

        # Include all enabled port checkboxes
        for port in sorted(enabled_ports, key=int):
            form_data.append(('rpport_ChkPortActive', '?%s' % port))

        # Include all port names
        for field, value in port_names.items():
            form_data.append((field, value))

        # Include all port speeds
        for field, value in port_speeds.items():
            form_data.append((field, value))

        # Add apply button - GS1915: rpport_HidBtnNum
        form_data.append(('rpport_HidBtnNum', '1'))

        code, response = self.post_form('/Forms/rpport_1', form_data)
        if code == 200:
            return True, 'Port %s configured' % port_id
        return False, 'Failed to configure port %s' % port_id

    def _configure_port_gs1920(self, port_id, config):
        """Configure port on GS1920 using read-modify-write pattern.

        IMPORTANT: This method reads current state first and preserves all
        existing settings to prevent accidentally disabling all ports.
        """
        # STEP 1: READ current port page
        content = self.get_page('/rpPort.html')

        # Parse all currently enabled ports (checkboxes)
        enabled_ports = set()
        for match in re.finditer(
            r'<INPUT[^>]*NAME="rpPort_Chk_PortActive"[^>]*VALUE="\?(\d+)"[^>]*>',
            content, re.IGNORECASE
        ):
            if 'CHECKED' in match.group(0).upper():
                enabled_ports.add(match.group(1))

        # Parse all port names
        port_names = self._parse_form_inputs(content, r'rpPort_Ipt_PortName\?\d+')

        # Parse all port speeds
        port_speeds = self._parse_form_selects(content, r'rpPort_Slt_Speed\?\d+')

        # STEP 2: MODIFY - apply requested changes
        port_id_str = str(port_id)

        if config.get('enabled') is not None:
            if config['enabled']:
                enabled_ports.add(port_id_str)
            else:
                enabled_ports.discard(port_id_str)

        if config.get('name') is not None:
            port_names['rpPort_Ipt_PortName?%s' % port_id_str] = config['name']

        if config.get('speed') is not None:
            speed_map = {
                'auto': '00000000',
                '10m-half': '00000006',
                '10m-full': '00000007',
                '100m-half': '00000004',
                '100m-full': '00000005',
                '1g-full': '00000003',
            }
            port_speeds['rpPort_Slt_Speed?%s' % port_id_str] = speed_map.get(
                config['speed'], '00000000'
            )

        # STEP 3: WRITE - build form data with ALL current state
        form_data = []

        # Include all enabled port checkboxes
        for port in sorted(enabled_ports, key=int):
            form_data.append(('rpPort_Chk_PortActive', '?%s' % port))

        # Include all port names
        for field, value in port_names.items():
            form_data.append((field, value))

        # Include all port speeds
        for field, value in port_speeds.items():
            form_data.append((field, value))

        # Add apply button
        form_data.append(('rpPort_HidBtn_NumID', '1'))

        code, response = self.post_form('/Forms/rpPort_1', form_data)
        if code == 200:
            return True, 'Port %s configured' % port_id
        return False, 'Failed to configure port %s' % port_id

    def _configure_port_gs1900(self, port_id, config):
        """Configure port on GS1900."""
        data = {'cmd': 768, 'port': port_id}

        if config.get('enabled') is not None:
            data['state'] = '1' if config['enabled'] else '0'

        if config.get('name') is not None:
            data['desc'] = config['name']

        if data:
            return self.post_form(768, data)
        return None

    def configure_system(self, config):
        """Configure system settings."""
        model = self.detect_model()

        if model == 'gs1900':
            return self._configure_system_gs1900(config)
        elif model == 'gs1915':
            return self._configure_system_gs1915(config)
        else:  # gs1920
            return self._configure_system_gs1920(config)

    def _configure_system_gs1915(self, config):
        """Configure system on GS1915 using read-modify-write pattern.

        Supports: hostname, location, contact
        """
        # STEP 1: READ current state from rpgeneral.html (lowercase)
        content = self.get_page('/rpgeneral.html')

        # Parse current values - GS1915 uses lowercase names like rpgeneral_IptSystemName
        current = self._parse_form_inputs(content, r'rpgeneral_Ipt\w+')
        current_selects = self._parse_form_selects(content, r'rpgeneral_Slt\w+')

        # STEP 2: MODIFY - apply requested changes
        if config.get('hostname') is not None:
            current['rpgeneral_IptSystemName'] = config['hostname']

        if config.get('location') is not None:
            current['rpgeneral_IptLocation'] = config['location']

        if config.get('contact') is not None:
            current['rpgeneral_IptContactName'] = config['contact']

        # STEP 3: WRITE - build form with all current state
        form_data = []

        # Add all text inputs
        for field, value in current.items():
            form_data.append((field, value))

        # Add all selects
        for field, value in current_selects.items():
            form_data.append((field, value))

        # Add apply button - GS1915: rpgeneral_HidBtnNum
        form_data.append(('rpgeneral_HidBtnNum', '1'))

        code, response = self.post_form('/Forms/rpgeneral_1', form_data)
        if code == 200:
            return True, 'System configured'
        return False, 'Failed to configure system'

    def _configure_system_gs1920(self, config):
        """Configure system on GS1920 using read-modify-write pattern.

        Supports: hostname, location, contact, ntp_servers, timezone
        """
        # STEP 1: READ current state from rpGeneral.html
        content = self.get_page('/rpGeneral.html')

        # Parse current values
        current = self._parse_form_inputs(content, r'rpGeneral_Ipt_\w+')
        current_selects = self._parse_form_selects(content, r'rpGeneral_Slt_\w+')

        # STEP 2: MODIFY - apply requested changes
        if config.get('hostname') is not None:
            current['rpGeneral_Ipt_SystemName'] = config['hostname']

        if config.get('location') is not None:
            current['rpGeneral_Ipt_Location'] = config['location']

        if config.get('contact') is not None:
            current['rpGeneral_Ipt_ContactName'] = config['contact']

        # NTP server configuration
        if config.get('ntp_servers') is not None:
            servers = config['ntp_servers']
            if len(servers) > 0:
                current['rpGeneral_Ipt_TimeSvrIP?1'] = servers[0]
            if len(servers) > 1:
                current['rpGeneral_Ipt_TimeSvrIP?2'] = servers[1]
            if len(servers) > 2:
                current['rpGeneral_Ipt_TimeSvrIP?3'] = servers[2]

        if config.get('timezone') is not None:
            # Timezone is a select field - map common values
            tz_map = {
                'UTC': '00000018',
                'UTC+0': '00000018',
                'UTC-5': '00000013',  # EST
                'UTC-6': '00000012',  # CST
                'UTC-7': '00000011',  # MST
                'UTC-8': '00000010',  # PST
                'UTC+1': '00000019',
                'UTC+8': '00000020',
            }
            tz_val = tz_map.get(config['timezone'], config['timezone'])
            current_selects['rpGeneral_Slt_TimeZone'] = tz_val

        # STEP 3: WRITE - build form with all current state
        form_data = []

        # Add all text inputs
        for field, value in current.items():
            form_data.append((field, value))

        # Add all selects
        for field, value in current_selects.items():
            form_data.append((field, value))

        # Add apply button
        form_data.append(('rpGeneral_HidBtn_NumID', '1'))

        code, response = self.post_form('/Forms/rpGeneral_1', form_data)
        if code == 200:
            return True, 'System configured'
        return False, 'Failed to configure system'

    def _configure_system_gs1900(self, config):
        """Configure system on GS1900."""
        data = {'cmd': 512}

        if config.get('hostname') is not None:
            data['system_name'] = config['hostname']

        if config.get('location') is not None:
            data['system_location'] = config['location']

        if config.get('contact') is not None:
            data['system_contact'] = config['contact']

        if data:
            data['sysSubmit'] = 'Apply'
            return self.post_form(512, data)
        return None

    def configure_syslog(self, config):
        """Configure syslog settings.

        Args:
            config: Dict with keys:
                - enabled: bool, enable/disable syslog globally
                - servers: list of dicts with 'address' and optional 'port'

        Returns:
            Tuple of (success, message)
        """
        model = self.detect_model()
        if model == 'gs1900':
            return False, 'Syslog config not implemented for GS1900'
        elif model == 'gs1915':
            return False, 'Syslog config not implemented for GS1915'
        else:  # gs1920
            return self._configure_syslog_gs1920(config)

    def _configure_syslog_gs1920(self, config):
        """Configure syslog on GS1920 using read-modify-write pattern."""
        # STEP 1: READ current syslog setup page
        content = self.get_page('/rpSyslog.html')

        # Parse global syslog enabled checkbox
        global_enabled = 'CHECKED' in re.search(
            r'<INPUT[^>]*NAME="rpSyslog_Chk_GlobalActive"[^>]*>',
            content, re.IGNORECASE
        ).group(0).upper() if re.search(
            r'<INPUT[^>]*NAME="rpSyslog_Chk_GlobalActive"[^>]*>',
            content, re.IGNORECASE
        ) else False

        # Parse type active checkboxes (categories 1-5)
        type_active = self._parse_form_checkboxes(content, 'rpSyslog_Chk_TypeActive')

        # Parse facilities
        facilities = self._parse_form_selects(content, r'rpSyslog_Slt_Facility\?\d+')

        # STEP 2: MODIFY
        if config.get('enabled') is not None:
            global_enabled = config['enabled']

        # STEP 3: BUILD form data
        form_data = []

        if global_enabled:
            form_data.append(('rpSyslog_Chk_GlobalActive', 'on'))

        for val in type_active:
            form_data.append(('rpSyslog_Chk_TypeActive', val))

        for field, val in facilities.items():
            form_data.append((field, val))

        form_data.append(('rpSyslog_HidBtn_NumID', '1'))

        code, response = self.post_form('/Forms/rpSyslog_1', form_data)

        # If servers are specified, add them via the server form
        if config.get('servers') and code == 200:
            for server in config['servers']:
                self._add_syslog_server_gs1920(server)

        if code == 200:
            return True, 'Syslog configured'
        return False, 'Failed to configure syslog'

    def _add_syslog_server_gs1920(self, server):
        """Add a syslog server on GS1920."""
        form_data = [
            ('rpSyslog_Toggle_Ipt_ServerAddr', server.get('address', '')),
            ('rpSyslog_Toggle_Ipt_UdpPort', str(server.get('port', 514))),
            ('rpSyslog_HidBtn_ServerNumID', '1'),  # Add
            ('rpSyslog_HidBtn_ServerIndexID', '0'),
        ]
        return self.post_form('/Forms/rpSyslog_2', form_data)

    def configure_lag(self, config):
        """Configure LAG/trunk groups.

        Args:
            config: Dict with keys:
                - groups: dict of group_id -> {enabled, members, criteria}

        Returns:
            Tuple of (success, message)
        """
        model = self.detect_model()
        if model == 'gs1900':
            return False, 'LAG config not implemented for GS1900'
        elif model == 'gs1915':
            return False, 'LAG config not implemented for GS1915'
        else:  # gs1920
            return self._configure_lag_gs1920(config)

    def _configure_lag_gs1920(self, config):
        """Configure LAG on GS1920 using read-modify-write pattern."""
        # STEP 1: READ current LAG setting page
        content = self.get_page('/rpLacpsetting.html')

        # Parse enabled groups
        enabled_groups = set()
        for match in re.finditer(
            r'<INPUT[^>]*NAME="rpLacpsetting_Chk_GroupActive"[^>]*VALUE="\?(\d+)"[^>]*>',
            content, re.IGNORECASE
        ):
            if 'CHECKED' in match.group(0).upper():
                enabled_groups.add(match.group(1))

        # Parse criteria selects
        criteria = self._parse_form_selects(content, r'rpLacpsetting_Slt_Criteria\?\d+,\d+')

        # Parse port-to-group assignments
        port_groups = self._parse_form_selects(content, r'rpLacpsetting_Slt_Group\?\d+')

        # STEP 2: MODIFY based on config
        groups_config = config.get('groups', {})
        for group_id, group_cfg in groups_config.items():
            group_id_str = str(group_id)

            if group_cfg.get('enabled', True):
                enabled_groups.add(group_id_str)
            else:
                enabled_groups.discard(group_id_str)

            # Set criteria for this group
            if group_cfg.get('criteria'):
                criteria_key = 'rpLacpsetting_Slt_Criteria?%s,1' % group_id_str
                criteria[criteria_key] = group_cfg['criteria']

            # Assign members to this group
            if group_cfg.get('members'):
                group_name = 'T%s' % group_id_str
                for port in group_cfg['members']:
                    port_key = 'rpLacpsetting_Slt_Group?%s' % port
                    port_groups[port_key] = group_name

        # STEP 3: BUILD form data
        form_data = []

        for group in sorted(enabled_groups, key=int):
            form_data.append(('rpLacpsetting_Chk_GroupActive', '?%s' % group))

        for field, val in criteria.items():
            form_data.append((field, val))

        for field, val in port_groups.items():
            form_data.append((field, val))

        form_data.append(('rpLacpsetting_HidBtn_NumID', '1'))

        code, response = self.post_form('/Forms/rpLacpsetting_1', form_data)
        if code == 200:
            return True, 'LAG configured'
        return False, 'Failed to configure LAG'

    def get_capabilities(self):
        """Return device capabilities."""
        model = self.detect_model()
        return {
            'rpc': ['get_page', 'post_form', 'get_system_info', 'get_ports_info', 'get_vlans_info'],
            'network_api': 'httpapi',
            'device_info': {
                'network_os': 'zyxel',
                'network_os_platform': model,
                'model': model,
            },
            'device_operations': {
                'supports_commit': False,
                'supports_replace': False,
                'supports_rollback': False,
                'supports_defaults': False,
                'supports_onbox_diff': False,
                'supports_generate_diff': False,
                'supports_multiline_delimiter': False,
                'supports_diff_match': False,
                'supports_diff_ignore_lines': False,
                'supports_config_replace': False,
                'supports_admin': False,
                'supports_commit_comment': False,
            }
        }

