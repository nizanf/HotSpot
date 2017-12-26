from django.conf.urls import url

from . import views
app_name = 'polls'

urlpatterns = [
    url(r'^$', views.call_login, name='call_login'),
    url(r'^is_login/$', views.login, name='login'),
    url(r'^homepage/$', views.call_homepage, name='homepage'),
    url(r'^register/$', views.call_register, name='call_register'),
    url(r'^is_register/$', views.register, name='register'),

]


