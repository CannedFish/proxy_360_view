# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # Keystone
    url(r'^v3/auth/tokens$', views.TokenView.as_view()),
    url(r'^v3/domains$', views.DomainView.as_view()),
    url(r'^v3/users$', views.UserView.as_view()),
    url(r'^v3/projects$', views.ProjectView.as_view()),
    url(r'^v3/role_assignments$', views.RoleAssignView.as_view()),
    # Nova
    url(r'^([^/]+/)*?v2.1/((?P<tenant_id>[^/]+)/)*?servers$', views.ServerView.as_view()),
    url(r'^([^/]+/)*?v2.1/((?P<tenant_id>[^/]+)/)*?servers/detail$', views.ServerDetailView.as_view())
]

