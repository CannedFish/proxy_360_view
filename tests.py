# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import logging

from django.test import TestCase

LOG = logging.getLogger(__name__)

class Proxy360TestCase(TestCase):
    def setUp(self):
        self.url = 'http://localhost:9000'
        self.catalog = {}
        self.token = ''

    def _test_tokens(self):
        url = self.url + '/v3/auth/tokens'
        data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "id": "feaf4b4e79764dc58a0bf784cb061bbd",
                            "password": "123456"
                        }
                    }
                },
                "scope": {
                    "project":{
                        "id": "c29d562503fe4dddb62d33a03a95415f"
                    }
                }
            }
        }
        res = requests.post(url
                , data=json.dumps(data)
                , headers={'Content-Type': 'application/json'})
        LOG.debug(res.headers)
        LOG.debug(res.content)
        for svc in res.json()['token']['catalog']:
            self.catalog[svc['name']] = svc
        self.token = res.headers.get('X-Subject-Token')
        self.assertEqual(res.status_code, 201)

    def _get(self, url, code):
        res = requests.get(url, headers={'X-Auth-Token': self.token})
        LOG.debug(res.content)
        self.assertEqual(res.status_code, code)

    def _test_domains(self):
        url = self.url + '/v3/domains'
        self._get(url, 200)

    def _test_users(self):
        url = self.url + '/v3/users'
        self._get(url, 200)

    def _test_projects(self):
        url = self.url + '/v3/projects'
        self._get(url, 200)

    def _test_role_assignments(self):
        url = self.url + '/v3/role_assignments'
        self._get(url, 200)

    def _test_servers(self):
        url = self.catalog['nova']['endpoints'][0]['url'] + '/servers'
        self._get(url, 200)

    def _test_servers_detail(self):
        url = self.catalog['nova']['endpoints'][0]['url'] + '/servers/detail'
        self._get(url, 200)

    def test_proxy(self):
        self._test_tokens()
        self._test_domains()
        self._test_users()
        self._test_projects()
        self._test_role_assignments()
        self._test_servers()
        self._test_servers_detail()

