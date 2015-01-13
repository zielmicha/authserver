from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       (r'^grappelli/', include('grappelli.urls')),
                       (r'^admin/',  include(admin.site.urls)),
                       url(r'^api/', include('authapi.urls')),
                       url(r'^setpassword/', include('setpassword.urls')),
)
