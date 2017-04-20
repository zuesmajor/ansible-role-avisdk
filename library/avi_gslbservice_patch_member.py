#!/usr/bin/python
"""
# Created on Aug 12, 2016
#
# @author: Gaurav Rastogi (grastogi@avinetworks.com) GitHub ID: grastogi23
#
# module_check: supported
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
#
"""

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.0'}

DOCUMENTATION = '''
---
module: avi_api
author: Gaurav Rastogi (grastogi@avinetworks.com)

short_description: Avi API Module
description:
    - This module can be used for calling any resources defined in Avi REST API. U(https://avinetworks.com/)
    - This module is useful for invoking HTTP Patch methods and accessing resources that do not have an REST object associated with them.
version_added: 2.3
requirements: [ avisdk ]
options:
    data:
        description:
            - HTTP body of GSLB Service Member in YAML or JSON format.
    params:
        description:
            - Query parameters passed to the HTTP API.
    name:
        description:
            - Name of the GSLB Service
        required: true
    state:
        description:
            - The state that should be applied to the member. Member is
            - identified using field member.ip.addr.
        default: present
        choices: ["absent","present"]
extends_documentation_fragment:
    - avi
'''

EXAMPLES = '''
  - name: Patch GSLB Service to add a new member and group
    avi_gslbservice_patch_member:
      controller: '{{ controller }}'
      password: '{{ password }}'
      username: '{{ username }}'
      name: gs-3
      data:
        group:
          name: newfoo
          priority: 60
          members:
            - enabled: true
              ip:
                addr:  10.30.10.66
                type: V4
              ratio: 3
      api_version: 16.4
  - name: Patch GSLB Service to delete an existing member
    avi_gslbservice_patch_member:
      controller: '{{ controller }}'
      password: '{{ password }}'
      username: '{{ username }}'
      name: gs-3
      state: absent
      api_version: 16.4
      data:
        group:
          name: newfoo
          members:
            - enabled: true
              ip:
                addr:  10.30.10.68 #"{{ vs.obj.ip_address.addr }}"
                type: V4
              ratio: 3
'''


RETURN = '''
obj:
    description: Avi REST resource
    returned: success, changed
    type: dict
'''

import json
import time
from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy

HAS_AVI = True
try:
    from avi.sdk.avi_api import ApiSession, ObjectNotFound
    from avi.sdk.utils.ansible_utils import (
        avi_obj_cmp, cleanup_absent_fields, avi_common_argument_spec,
        ansible_return, AviCheckModeResponse)
except ImportError:
    HAS_AVI = False


def delete_member(module, check_mode, api, tenant, tenant_uuid,
                  existing_obj, data, api_version):
    members = data.get('group', {}).get('members', [])
    patched_member_ids = set([m['ip']['addr'] for m in members])
    changed = False
    rsp = None

    if existing_obj and patched_member_ids:
        groups = [group for group in existing_obj.get('groups', [])
                  if group['name'] == data['group']['name']]
        if groups:
            changed = any([(lambda g: g['ip']['addr'] in patched_member_ids)(m)
                          for m in groups[0].get('members', [])])
    if check_mode or not changed:
        return changed, rsp
    # should not come here if not found
    group = groups[0]
    new_members = [m for m in group.get('members', [])
                   if m['ip']['addr'] not in patched_member_ids]
    group['members'] = new_members
    # remove the members that are part of the list
    # update the object
    # added api version for AVI api call.
    rsp = api.put('gslbservice/%s' % existing_obj['uuid'], data=existing_obj,
                  tenant=tenant, tenant_uuid=tenant_uuid, api_version=api_version)
    return changed, rsp


def add_member(module, check_mode, api, tenant, tenant_uuid,
               existing_obj, data, name, api_version):
    rsp = None
    if not existing_obj:
        # create the object
        changed = True
        if check_mode:
            rsp = AviCheckModeResponse(obj=None)
        else:
            # creates group with single member
            req = {'name': name,
                   'groups': [data['group']]
                   }
            # added api version for AVI api call.
            rsp = api.post('gslbservice', data=req, tenant=tenant,
                           tenant_uuid=tenant_uuid, api_version=api_version)
    else:
        # found GSLB object
        req = deepcopy(existing_obj)
        if 'groups' not in req:
            req['groups'] = []
        groups = [group for group in req['groups']
                  if group['name'] == data['group']['name']]
        if not groups:
            # did not find the group
            req['groups'].append(data['group'])
        else:
            # just update the existing group with members
            group = groups[0]
            group_info_wo_members = deepcopy(group)
            del group_info_wo_members['members']
            group.update(group_info_wo_members)
            if 'members' not in group:
                group['members'] = []
            new_members = []
            for patch_member in data['group'].get('members', []):
                found = False
                for m in group['members']:
                    if m['ip']['addr'] == patch_member['ip']['addr']:
                        found = True
                        break
                if not found:
                    new_members.append(patch_member)
                else:
                    m.update(patch_member)
            # add any new members
            group['members'].extend(new_members)
        cleanup_absent_fields(req)
        changed = not avi_obj_cmp(req, existing_obj)
        if changed and not check_mode:
            obj_path = '%s/%s' % ('gslbservice', existing_obj['uuid'])
            # added api version for AVI api call.
            rsp = api.put(obj_path, data=req, tenant=tenant,
                          tenant_uuid=tenant_uuid, api_version=api_version)
    return changed, rsp


def main():
    argument_specs = dict(
        params=dict(type='dict'),
        data=dict(type='dict'),
        name=dict(type='str', required=True),
        state=dict(default='present',
                   choices=['absent', 'present'])
        )
    argument_specs.update(avi_common_argument_spec())
    module = AnsibleModule(argument_spec=argument_specs)

    if not HAS_AVI:
        return module.fail_json(msg=(
            'Avi python API SDK (avisdk) is not installed. '
            'For more details visit https://github.com/avinetworks/sdk.'))
    tenant_uuid = module.params.get('tenant_uuid', None)
    api = ApiSession.get_session(
        module.params['controller'], module.params['username'],
        module.params['password'], tenant=module.params['tenant'],
        tenant_uuid=tenant_uuid)
    tenant = module.params.get('tenant', '')
    params = module.params.get('params', None)
    data = module.params.get('data', None)
    gparams = deepcopy(params) if params else {}
    gparams.update({'include_refs': '', 'include_name': ''})
    name = module.params.get('name', '')
    state = module.params['state']
    # Get the api version from module.
    api_version = module.params.get('api_version', '16.4')
    """
    state: present
    1. Check if the GSLB service is present
    2.    If not then create the GSLB service with the member
    3. Check if the group exists
    4.    if not then create the group with the member
    5. Check if the member is present
          if not then add the member
    state: absent
    1. check if GSLB service is present if not then exit
    2. check if group is present. if not then exit
    3. check if member is present. if present then remove it.
    """
    obj_type = 'gslbservice'
    # Added api version to call
    existing_obj = api.get_object_by_name(
        obj_type, name, tenant=tenant, tenant_uuid=tenant_uuid,
        params={'include_refs': '', 'include_name': ''}, api_version=api_version)
    check_mode = module.check_mode
    if state == 'absent':
        # Added api version to call
        changed, rsp = delete_member(module, check_mode, api, tenant,
                                     tenant_uuid, existing_obj, data, api_version)
    else:
        # Added api version to call
        changed, rsp = add_member(module, check_mode, api, tenant, tenant_uuid,
                                  existing_obj, data, name, api_version)
    if check_mode or not changed:
        return module.exit_json(changed=changed, obj=existing_obj)
    return ansible_return(module, rsp, changed, req=data)


if __name__ == '__main__':
    main()