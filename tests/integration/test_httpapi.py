#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration test for Zyxel HTTP API connection to real switches."""

import random
import re
import requests
import urllib3
urllib3.disable_warnings()


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


class ZyxelTestClient:
    """Test client for Zyxel switches."""
    
    def __init__(self, host, username, password, model):
        self.host = host
        self.username = username
        self.password = password
        self.model = model.lower()
        self.session = requests.Session()
        self.session.verify = False
        self.auth_id = None
    
    def login(self):
        """Login to the switch."""
        if self.model == 'gs1900':
            return self._login_gs1900()
        elif self.model == 'gs1915':
            return self._login_gs1915()
        else:
            return self._login_gs1920()
    
    def _login_gs1920(self):
        resp = self.session.post(
            f'https://{self.host}/Forms/login_1',
            data={
                'rpAuthForm_Ipt_UserName': self.username,
                'rpAuthForm_Ipt_Password': self.password
            },
            allow_redirects=False
        )
        return resp.status_code in [200, 302, 303]
    
    def _login_gs1915(self):
        resp = self.session.post(
            f'https://{self.host}/Forms/login_1',
            data={
                'rpAuthForm_IptTextUsername': self.username,
                'rpAuthForm_IptTextPassword': self.password
            },
            allow_redirects=False
        )
        return resp.status_code in [200, 302, 303]
    
    def _login_gs1900(self):
        encoded_pw = encode_gs1900_password(self.password)
        resp = self.session.post(
            f'https://{self.host}/cgi-bin/dispatcher.cgi',
            data={'username': self.username, 'password': encoded_pw, 'login': 'true'}
        )
        if resp.status_code == 200:
            self.auth_id = resp.text.strip()
            verify = self.session.post(
                f'https://{self.host}/cgi-bin/dispatcher.cgi',
                data={'authId': self.auth_id, 'login_chk': 'true'}
            )
            return 'OK' in verify.text
        return False
    
    def get_system_info(self):
        """Get system information."""
        if self.model == 'gs1900':
            resp = self.session.get(f'https://{self.host}/cgi-bin/dispatcher.cgi?cmd=512')
        elif self.model == 'gs1915':
            resp = self.session.get(f'https://{self.host}/rpsysinfo.html')
        else:  # gs1920
            resp = self.session.get(f'https://{self.host}/rpSysinfo.html')
        return resp.text

    def get_port_config(self):
        """Get port configuration."""
        if self.model == 'gs1900':
            resp = self.session.get(f'https://{self.host}/cgi-bin/dispatcher.cgi?cmd=768')
        elif self.model == 'gs1915':
            resp = self.session.get(f'https://{self.host}/rpport.html')
        else:  # gs1920
            resp = self.session.get(f'https://{self.host}/rpPort.html')
        return resp.text

    def get_vlan_config(self):
        """Get VLAN configuration."""
        if self.model == 'gs1900':
            resp = self.session.get(f'https://{self.host}/cgi-bin/dispatcher.cgi?cmd=1282')
        elif self.model == 'gs1915':
            resp = self.session.get(f'https://{self.host}/rpvlantag.html')
        else:  # gs1920
            resp = self.session.get(f'https://{self.host}/rpVlan.html')
        return resp.text


def test_switch(name, host, model, username, password):
    """Test a single switch."""
    print(f"\n{'='*60}")
    print(f"Testing {name} ({model}) at {host}")
    print('='*60)
    
    client = ZyxelTestClient(host, username, password, model)
    
    # Test login
    print("\n[1] Testing login...", end=" ")
    if client.login():
        print("SUCCESS")
    else:
        print("FAILED")
        return False
    
    # Test system info
    print("[2] Getting system info...", end=" ")
    sys_info = client.get_system_info()
    print(f"OK ({len(sys_info)} bytes)")
    
    # Test port config
    print("[3] Getting port config...", end=" ")
    port_config = client.get_port_config()
    print(f"OK ({len(port_config)} bytes)")
    
    # Test VLAN config
    print("[4] Getting VLAN config...", end=" ")
    vlan_config = client.get_vlan_config()
    print(f"OK ({len(vlan_config)} bytes)")
    
    print(f"\n[PASS] {name} tests completed successfully")
    return True


if __name__ == '__main__':
    import os

    # Get credentials from environment variables
    USERNAME = os.environ.get('ZYXEL_USERNAME', 'admin')
    PASSWORD = os.environ.get('ZYXEL_PASSWORD')

    if not PASSWORD:
        print("ERROR: ZYXEL_PASSWORD environment variable not set")
        print("Usage: ZYXEL_PASSWORD=yourpassword python test_httpapi.py")
        exit(1)

    # Get switches from environment or use defaults
    # Format: name:host:model,name:host:model,...
    switches_env = os.environ.get('ZYXEL_SWITCHES')
    if switches_env:
        switches = []
        for switch in switches_env.split(','):
            parts = switch.strip().split(':')
            if len(parts) == 3:
                switches.append(tuple(parts))
    else:
        # Default example switches - update these for your environment
        switches = [
            ('GS1920-24HP', '192.168.1.10', 'gs1920'),
            ('GS1915-24EP', '192.168.1.11', 'gs1915'),
            ('GS1900-8HP', '192.168.1.12', 'gs1900'),
        ]

    results = []
    for name, host, model in switches:
        result = test_switch(name, host, model, USERNAME, PASSWORD)
        results.append((name, result))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

