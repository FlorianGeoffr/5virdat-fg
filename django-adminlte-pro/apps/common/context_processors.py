# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings

def get_settings(request):
    return { 'settings': settings }
