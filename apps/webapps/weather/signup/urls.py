from django.conf.urls import url

from . import views

app_name = 'signup'

urlpatterns = [
    url(r'^$', views.index, name='signup'),
    url(r'^confirm/$', views.confirm, name='confirm'),
]