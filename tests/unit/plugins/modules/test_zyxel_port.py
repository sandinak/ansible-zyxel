# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for zyxel_port module (HTTP API version).

Note: This module is currently stubbed as HTTP API support is not yet implemented.
These tests verify the module can be imported and has the expected structure.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest


class TestPortModule:
    """Tests for zyxel_port module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_port
        assert hasattr(zyxel_port, 'main')

