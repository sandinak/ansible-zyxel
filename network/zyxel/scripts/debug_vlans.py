#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script to fetch and analyze VLAN pages from switch."""
from __future__ import print_function

import sys
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_vlans.py <switch_ip> <password>")
        sys.exit(1)

    switch_ip = sys.argv[1]
    password = sys.argv[2]
    username = "admin"

    session = requests.Session()
    session.verify = False

    # Login
    login_url = "https://{0}/Forms/login_1".format(switch_ip)
    login_data = {
        'rpAuthForm_Ipt_UserName': username,
        'rpAuthForm_Ipt_Password': password,
    }
    print("Logging in to {0}...".format(switch_ip))
    resp = session.post(login_url, data=login_data, allow_redirects=True)
    print("Login: {0}, URL: {1}".format(resp.status_code, resp.url))

    if 'login' in resp.url.lower():
        print("Login failed!")
        sys.exit(1)

    # Fetch VLAN tag page
    print("\n=== Fetching rpVlantag.html ===")
    resp = session.get("https://{0}/rpVlantag.html".format(switch_ip))
    print("Status: {0}, Length: {1}".format(resp.status_code, len(resp.text)))

    # Save for inspection
    with open('/tmp/debug_vlantag.html', 'w') as f:
        f.write(resp.text)
    print("Saved to /tmp/debug_vlantag.html")

    # Parse VLANs from tag page
    # Structure: checkbox VALUE="?N", VID, status-on/off, Name
    print("\n=== Parsing VLANs from tag page ===")

    # Simpler approach: find all checkbox values and VID cells
    # Pattern: VALUE="?N" followed by VID in next <td>
    checkbox_pattern = r'NAME="rpVlantag_Chk_TabDel"\s+VALUE="\?(\d+)"'
    checkboxes = re.findall(checkbox_pattern, resp.text, re.IGNORECASE)
    print("Found {0} VLAN table indexes: {1}".format(len(checkboxes), checkboxes))

    # Now find VID and Name for each row
    # Each VLAN row structure:
    # <INPUT ... NAME="rpVlantag_Chk_TabDel" VALUE="?N">
    #   <label>...</label>
    # </td>
    # <td>VID</td>
    # <td><span class="status-on/off">ON/OFF</span></td>
    # <td style="text-align:left" class="word-break">NAME</td>
    row_pattern = r'NAME="rpVlantag_Chk_TabDel"\s+VALUE="\?(\d+)".*?</td>\s*<td[^>]*>(\d+)\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>\s*(\S[^<]*)</td>'
    matches = re.findall(row_pattern, resp.text, re.IGNORECASE | re.DOTALL)

    print("Found {0} VLANs:".format(len(matches)))
    vlans = []
    for idx, vid, name in matches:
        vlans.append((idx, vid, name.strip()))
        print("  Index={0}, VID={1}, Name='{2}'".format(idx, vid, name.strip()))

    # Get port PVID assignments from vlanport page
    print("\n=== Fetching rpVlanport.html (port-VLAN mapping) ===")
    resp = session.get("https://{0}/rpVlanport.html".format(switch_ip))
    print("Status: {0}, Length: {1}".format(resp.status_code, len(resp.text)))

    # Parse PVID for each port
    pvid_pattern = r'NAME="rpVlanport_Ipt_PVID\?(\d+)"[^>]*VALUE="(\d+)"'
    pvid_matches = re.findall(pvid_pattern, resp.text, re.IGNORECASE)
    print("\nPort PVID assignments:")
    pvid_by_port = {}
    for port, pvid in pvid_matches:
        pvid_by_port[port] = pvid

    # Group ports by PVID
    ports_by_vlan = {}
    for port, pvid in pvid_by_port.items():
        if pvid not in ports_by_vlan:
            ports_by_vlan[pvid] = []
        ports_by_vlan[pvid].append(int(port))

    for vid in sorted(ports_by_vlan.keys(), key=int):
        ports = sorted(ports_by_vlan[vid])
        print("  VLAN {0}: ports {1}".format(vid, ports))

    # Now fetch each VLAN's port membership details
    print("\n=== Checking individual VLAN port membership ===")
    for idx, vid, name in vlans:
        # Click on VLAN row to get edit form with port membership
        # NumID=5 shows the edit form for that VLAN
        detail_data = {
            'rpVlantag_HidBtn_NumID': '5',
            'rpVlantag_HidBtn_IndexID': idx,
        }
        resp = session.post("https://{0}/Forms/rpVlantag_1".format(switch_ip), data=detail_data)
        if resp.status_code == 200:
            with open('/tmp/debug_vlan_{0}.html'.format(vid), 'w') as f:
                f.write(resp.text)

            # Parse port membership - look for Fixed/Forbidden/Normal selections
            # Port rows have select elements with options: Fixed, Forbidden, (Egress), Normal
            fixed_pattern = r'NAME="rpVlantag_Toggle_Slt_Port\?(\d+)"[^>]*>.*?<option[^>]*value="1"[^>]*selected'
            fixed_ports = re.findall(fixed_pattern, resp.text, re.IGNORECASE | re.DOTALL)

            # Also check for "Tagged" checkbox
            tagged_pattern = r'NAME="rpVlantag_Toggle_Chk_Tagging"[^>]*VALUE="\?(\d+)"[^>]*CHECKED'
            is_tagged = re.findall(tagged_pattern, resp.text, re.IGNORECASE)

            untagged_ports = []
            tagged_ports = []
            if vid in ports_by_vlan:
                untagged_ports = sorted(ports_by_vlan[vid])

            print("VLAN {0} ({1}): fixed_ports={2}, is_tagged={3}, untagged_from_pvid={4}".format(
                vid, name, fixed_ports[:5] if len(fixed_ports) > 5 else fixed_ports,
                bool(is_tagged), untagged_ports[:5] if len(untagged_ports) > 5 else untagged_ports))


if __name__ == '__main__':
    main()

