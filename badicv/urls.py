'''
Created on 19/10/2017

@author: Admin
'''
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^experience/$', views.experience_search, name='experience search'),
    url(r'^experience/(?P<experi_name>.+)/$', views.experience_description, 
        name='experience description'),
    url(r'^skill/$', views.skill_search, name='skill search'),
    url(r'^skill/(?P<skill_name>.+)/$', views.skill_description, 
        name='skill description'),
    url(r'^referees/$', views.referee_list, name='referee list'),
]