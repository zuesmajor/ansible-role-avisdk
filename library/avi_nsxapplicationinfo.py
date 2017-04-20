#!/usr/bin/python
#
# Created on Aug 25, 2016
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: supported
# Avi Version: 17.1
#
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.0'}

DOCUMENTATION = '''
---
module: avi_nsxapplicationinfo
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: Module for setup of NsxApplicationInfo Avi RESTful Object
description:
    - This module is used to configure NsxApplicationInfo object
    - more examples at U(https://github.com/avinetworks/devops)
requirements: [ avisdk ]
version_added: "2.3"
options:
    state:
        description:
            - The state that should be applied on the entity.
        default: present
        choices: ["absent","present"]
    applicationProtocol:
        description:
            - Applicationprotocol of nsxapplicationinfo.
    name:
        description:
            - Name of the object.
        required: true
    nsx_object_id:
        description:
            - Nsx_object_id of nsxapplicationinfo.
    obj_uuid:
        description:
    typeName:
        description:
            - Typename of nsxapplicationinfo.
    url:
        description:
            - Avi controller URL of the object.
    uuid:
        description:
            - Unique object identifier of the object.
    value:
        description:
            - Value of nsxapplicationinfo.
extends_documentation_fragment:
    - avi
'''

EXAMPLES = """
- name: Example to create NsxApplicationInfo object
  avi_nsxapplicationinfo:
    controller: 10.10.25.42
    username: admin
    password: something
    state: present
    name: sample_nsxapplicationinfo
"""

RETURN = '''
obj:
    description: NsxApplicationInfo (api/nsxapplicationinfo) object
    returned: success, changed
    type: dict
'''

from pkg_resources import parse_version
from ansible.module_utils.basic import AnsibleModule
from avi.sdk.utils.ansible_utils import avi_common_argument_spec

HAS_AVI = True
try:
    import avi.sdk
    sdk_version = getattr(avi.sdk, '__version__', None)
    if ((sdk_version is None) or (sdk_version and
            (parse_version(sdk_version) < parse_version('16.3.5.post1')))):
        # It allows the __version__ to be '' as that value is used in development builds
        raise ImportError
    from avi.sdk.utils.ansible_utils import avi_ansible_api
except ImportError:
    HAS_AVI = False


def main():
    argument_specs = dict(
        state=dict(default='present',
                   choices=['absent', 'present']),
        applicationProtocol=dict(type='str',),
        name=dict(type='str', required=True),
        nsx_object_id=dict(type='str',),
        obj_uuid=dict(type='str',),
        typeName=dict(type='str',),
        url=dict(type='str',),
        uuid=dict(type='str',),
        value=dict(type='str',),
    )
    argument_specs.update(avi_common_argument_spec())
    module = AnsibleModule(
        argument_spec=argument_specs, supports_check_mode=True)
    if not HAS_AVI:
        return module.fail_json(msg=(
            'Avi python API SDK (avisdk>=16.3.5.post1) is not installed. '
            'For more details visit https://github.com/avinetworks/sdk.'))
    return avi_ansible_api(module, 'nsxapplicationinfo',
                           set([]))


if __name__ == '__main__':
    main()
