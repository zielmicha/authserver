from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^users$', 'authapi.views.users'),
    url(r'^auth$', 'authapi.views.auth'),
)
