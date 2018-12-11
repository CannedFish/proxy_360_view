# -*- coding: utf-8 -*-
import logging
import requests
import json
from urlparse import urlparse
import copy

from django.utils import six
from django.http import HttpResponse
from rest_framework.views import APIView

from sugon_api import settings

LOG = logging.getLogger(__name__)

def get_params(req):
    LOG.debug('query: %s' % req.query_params)
    if req.query_params:
        qp = req.query_params.copy()
        return six.iterlists(qp)

    return {}

def get_data(req):
    LOG.debug('data type: %s' % type(req.data))
    LOG.debug(req.data)
    if 'application/json' in req.content_type:
        return json.dumps(req.data)

    return req.data

def get_headers(req):
    LOG.debug('headers:\n%s' % req.META)

    # Added by Arthur
    if 'CONTENT_TYPE' in req.META:
        req.META['Content-Type'] = "application/json"
    if 'HTTP_X_AUTH_TOKEN' in req.META:
        req.META['X-Auth-Token'] = req.META['HTTP_X_AUTH_TOKEN']

    return req.META

def get_cookies(req):
    LOG.debug('cookies:\n%s' % req.COOKIES)
    return req.COOKIES

def proxy(req, url, *args, **kw):
    params = get_params(req)
    data = get_data(req)
    headers = get_headers(req)
    cookies = get_cookies(req)

    try:
        LOG.info('Proxy a %s to %s' % (req.method, url))
        return requests.request(req.method
                , url
                , params=params
                , data=data
                , headers=headers
                , cookies=cookies
                , timeout=5)

    except Exception, e:
        LOG.error(e)
        return None

class ProxyView(APIView):
    def _get_base_url(self):
        raise NotImplementedError('Must be implemented in child')

    def _proxy(self, req, *args, **kw):
        res = proxy(req, self._get_base_url()+req.META['PATH_INFO'])
        rsp = HttpResponse(res.text
                , status=res.status_code
                , content_type=res.headers.get('Content-Type'))
        rsp['x-openstack-request-id'] = res.headers.get('x-openstack-request-id')
        return rsp

    def get(self, req, *args, **kw):
        return self._proxy(req, *args, **kw)

    def post(self, req, *args, **kw):
        return self._proxy(req, *args, **kw)

catalog = {}

class IdentityView(ProxyView):
    def _create_auth_tokens(self, req):
        res = proxy(req, settings.PROXY_360_AUTH_URL+req.META['PATH_INFO'])
        if res is None:
            return HttpResponse('Error occured!', status=500)

        try:
            body = res.json()
            LOG.debug('catalog: %s' % json.dumps(catalog))
            LOG.debug('response body: %s' % json.dumps(body))
            for svc in body['token']['catalog']:
                LOG.debug(svc['name'])
                catalog[svc['name']] = copy.deepcopy(svc)
                for ep, ep_real in \
                        zip(svc['endpoints'], catalog[svc['name']]['endpoints']):
                    _url = urlparse(ep['url'])
                    ep["url"] = _url.scheme + '://' + settings.PROXY_LOCATION + _url.path
                    ep_real["host"] = _url.scheme + '://' + _url.netloc
                LOG.debug(svc['endpoints'])
            LOG.debug('catalog: %s' % json.dumps(catalog))
            proxy_res = HttpResponse(json.dumps(body), status=res.status_code)
            for k in [_ for _ in res.headers \
                    if _ in ['X-Subject-Token', 'Vary', 'Content-Type', \
                    'x-openstack-request-id']]:
                LOG.debug(k)
                proxy_res[k] = res.headers.get(k)
            return proxy_res
        except Exception, e:
            LOG.error(e)
            return HttpResponse(e, status=500)

    def _get_base_url(self):
        return settings.PROXY_360_AUTH_URL

    def post(self, req, *args, **kw):
        if req.META['PATH_INFO'].endswith('/auth/tokens'):
            return self._create_auth_tokens(req)
        return super(IdentityView, self).post(req, *args, **kw)

class ComputeView(ProxyView):
    def _get_base_url(self):
        host = catalog['nova']['endpoints'][0]['host']
        for ep in catalog['nova']['endpoints'][1:]:
            if ep['interface'] == 'internal':
                host = ep['host']
        return host

