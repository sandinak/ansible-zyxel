# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Documentation fragment for Zyxel modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    """Documentation fragment for Zyxel modules."""

    # Standard documentation fragment
    DOCUMENTATION = r'''
options: {}
notes:
  - Tested against Zyxel GS2220 series switches.
  - This module requires the C(ansible.netcommon) collection.
  - For more information on using Ansible to manage network devices see the
    L(Ansible Network Guide,https://docs.ansible.com/ansible/latest/network/index.html).
seealso:
  - name: Zyxel Switch Documentation
    description: Official Zyxel switch documentation
    link: https://www.zyxel.com/support/
'''

