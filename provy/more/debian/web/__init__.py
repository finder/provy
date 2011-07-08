#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roles in this namespace are meant to configure either Web Servers (apache, nginx) or Web App Servers (tornado, django, rails) in Debian distributions.
'''
from provy.more.debian.web.nginx import NginxRole
from provy.more.debian.web.tornado import TornadoRole
