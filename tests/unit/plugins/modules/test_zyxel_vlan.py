# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for zyxel_vlan module (HTTP API version)."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import patch, MagicMock

from ansible_collections.network.zyxel.plugins.modules.zyxel_vlan import (
    get_vlan_config,
    needs_update,
)


class TestGetVlanConfig:
    """Tests for get_vlan_config function."""

    @patch('ansible_collections.network.zyxel.plugins.modules.zyxel_vlan.get_connection')
    def test_get_vlan_not_found(self, mock_get_connection):
        """Test getting a VLAN that doesn't exist."""
        mock_conn = MagicMock()
        # get_vlans_info returns a dict keyed by VLAN ID
        mock_conn.get_vlans_info.return_value = {
            '1': {'name': 'Default', 'tagged_ports': [], 'untagged_ports': ['1', '2']}
        }
        mock_get_connection.return_value = mock_conn

        module = MagicMock()
        result = get_vlan_config(module, 100)
        assert result.get('exists') is False

    @patch('ansible_collections.network.zyxel.plugins.modules.zyxel_vlan.get_connection')
    def test_get_existing_vlan(self, mock_get_connection):
        """Test getting an existing VLAN."""
        mock_conn = MagicMock()
        # get_vlans_info returns a dict keyed by VLAN ID
        mock_conn.get_vlans_info.return_value = {
            '100': {'name': 'Management', 'tagged_ports': ['24'], 'untagged_ports': ['1', '2']}
        }
        mock_get_connection.return_value = mock_conn

        module = MagicMock()
        result = get_vlan_config(module, 100)
        assert result.get('exists') is True
        assert result.get('name') == 'Management'
        assert result.get('tagged_ports') == ['24']
        assert result.get('untagged_ports') == ['1', '2']


class TestNeedsUpdate:
    """Tests for needs_update function."""

    def test_no_update_needed(self):
        """Test when VLAN already matches desired state."""
        current = {
            'exists': True,
            'name': 'Management',
            'tagged_ports': ['24'],
            'untagged_ports': ['1', '2'],
        }
        params = {
            'name': 'Management',
            'tagged_ports': ['24'],
            'untagged_ports': ['1', '2'],
        }
        assert needs_update(current, params) is False

    def test_name_update_needed(self):
        """Test when VLAN name needs update."""
        current = {
            'exists': True,
            'name': 'OldName',
            'tagged_ports': [],
            'untagged_ports': [],
        }
        params = {
            'name': 'NewName',
            'tagged_ports': None,
            'untagged_ports': None,
        }
        assert needs_update(current, params) is True

    def test_tagged_ports_update_needed(self):
        """Test when tagged ports need update."""
        current = {
            'exists': True,
            'name': 'Test',
            'tagged_ports': ['24'],
            'untagged_ports': [],
        }
        params = {
            'name': 'Test',
            'tagged_ports': ['24', '25'],
            'untagged_ports': [],
        }
        assert needs_update(current, params) is True

    def test_untagged_ports_update_needed(self):
        """Test when untagged ports need update."""
        current = {
            'exists': True,
            'name': 'Test',
            'tagged_ports': [],
            'untagged_ports': ['1', '2'],
        }
        params = {
            'name': 'Test',
            'tagged_ports': [],
            'untagged_ports': ['1', '2', '3'],
        }
        assert needs_update(current, params) is True

    def test_empty_params_no_update(self):
        """Test when params match current state (empty lists)."""
        current = {
            'exists': True,
            'name': 'Test',
            'tagged_ports': [],
            'untagged_ports': [],
        }
        params = {
            'name': '',  # Empty name means don't change
            'tagged_ports': None,  # None becomes [] which matches current
            'untagged_ports': None,  # None becomes [] which matches current
        }
        assert needs_update(current, params) is False

