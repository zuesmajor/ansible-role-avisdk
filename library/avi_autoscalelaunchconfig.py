#!/usr/bin/python
#
# Created on Aug 25, 2016
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: supported
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: avi_autoscalelaunchconfig
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: Module for setup of AutoScaleLaunchConfig Avi RESTful Object
description:
    - This module is used to configure AutoScaleLaunchConfig object
    - more examples at U(https://github.com/avinetworks/devops)
requirements: [ avisdk ]
version_added: "2.4"
options:
    state:
        description:
            - The state that should be applied on the entity.
        default: present
        choices: ["absent","present"]
    aws:
        description:
            - Autoscaleawssettings settings for autoscalelaunchconfig.
    description:
        description:
            - User defined description for the object.
    image_id:
        description:
            - Unique id of the amazon machine image (ami)  or openstack vm id.
    mesos:
        description:
            - Autoscalemesossettings settings for autoscalelaunchconfig.
    name:
        description:
            - Name of the object.
        required: true
    openstack:
        description:
            - Autoscaleopenstacksettings settings for autoscalelaunchconfig.
    tenant_ref:
        description:
            - It is a reference to an object of type tenant.
    url:
        description:
            - Avi controller URL of the object.
    uuid:
        description:
            - Unique object identifier of the object.
extends_documentation_fragment:
    - avi
'''


EXAMPLES = '''
  - name: Create an Autoscale Launch configuration.
    avi_autoscalelaunchconfig:
      controller: ''
      username: ''
      password: ''
      image_id: default
      name: default-autoscalelaunchconfig
      tenant_ref: admin
'''
RETURN = '''
obj:
    description: AutoScaleLaunchConfig (api/autoscalelaunchconfig) object
    returned: success, changed
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from avi.sdk.utils.ansible_utils import avi_common_argument_spec
    from pkg_resources import parse_version
    import avi.sdk
    sdk_version = getattr(avi.sdk, '__version__', None)
    if ((sdk_version is None) or (sdk_version and
            (parse_version(sdk_version) < parse_version('17.1')))):
        # It allows the __version__ to be '' as that value is used in development builds
        raise ImportError
    from avi.sdk.utils.ansible_utils import avi_ansible_api
    HAS_AVI = True
except ImportError:
    HAS_AVI = False


def main():
    argument_specs = dict(
        state=dict(default='present',
                   choices=['absent', 'present']),
        aws=dict(type='dict',),
        description=dict(type='str',),
        image_id=dict(type='str',),
        mesos=dict(type='dict',),
        name=dict(type='str', required=True),
        openstack=dict(type='dict',),
        tenant_ref=dict(type='str',),
        url=dict(type='str',),
        uuid=dict(type='str',),
    )
    argument_specs.update(avi_common_argument_spec())
    module = AnsibleModule(
        argument_spec=argument_specs, supports_check_mode=True)
    if not HAS_AVI:
        return module.fail_json(msg=(
            'Avi python API SDK (avisdk>=17.1) is not installed. '
            'For more details visit https://github.com/avinetworks/sdk.'))
    return avi_ansible_api(module, 'autoscalelaunchconfig',
                           set([]))

if __name__ == '__main__':
    main()
