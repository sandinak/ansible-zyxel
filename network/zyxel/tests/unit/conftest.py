# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Pytest configuration for unit tests."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Set up the collection path structure for imports
# The collection is at network/zyxel, so we need to create the proper namespace
COLLECTION_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(COLLECTION_ROOT))

# Create ansible_collections namespace path
ansible_collections_path = os.path.join(WORKSPACE_ROOT)
if ansible_collections_path not in sys.path:
    sys.path.insert(0, ansible_collections_path)

# Also add the collection root for direct imports
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

# Create the namespace package structure
import types
if 'ansible_collections' not in sys.modules:
    ansible_collections = types.ModuleType('ansible_collections')
    ansible_collections.__path__ = [os.path.join(WORKSPACE_ROOT)]
    sys.modules['ansible_collections'] = ansible_collections

if 'ansible_collections.network' not in sys.modules:
    network = types.ModuleType('ansible_collections.network')
    network.__path__ = [os.path.join(WORKSPACE_ROOT, 'network')]
    sys.modules['ansible_collections.network'] = network

if 'ansible_collections.network.zyxel' not in sys.modules:
    zyxel = types.ModuleType('ansible_collections.network.zyxel')
    zyxel.__path__ = [COLLECTION_ROOT]
    sys.modules['ansible_collections.network.zyxel'] = zyxel


@pytest.fixture
def mock_module():
    """Create a mock AnsibleModule."""
    module = MagicMock()
    module.params = {}
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock()
    return module


@pytest.fixture
def mock_connection():
    """Create a mock connection object."""
    connection = MagicMock()
    connection.get = MagicMock(return_value='')
    connection.edit_config = MagicMock()
    return connection


@pytest.fixture
def mock_run_commands():
    """Create a mock for run_commands function."""
    with patch('ansible_collections.network.zyxel.plugins.module_utils.zyxel.run_commands') as mock:
        mock.return_value = ['']
        yield mock


@pytest.fixture
def mock_load_config():
    """Create a mock for load_config function."""
    with patch('ansible_collections.network.zyxel.plugins.module_utils.zyxel.load_config') as mock:
        mock.return_value = None
        yield mock

