from django.conf.urls import url

from . import views
app_name = 'polls'

urlpatterns = [
    url(r'^$', views.call_login, name='call_login'),
    url(r'^is_login/$', views.login_user, name='login'),

    url(r'^logout/$', views.logout_user, name='logout'),

    url(r'^homepage/$', views.call_homepage, name='homepage'),
    url(r'^register/$', views.call_register, name='call_register'),
    url(r'^is_register/$', views.register, name='register'),

    url(r'^report_parking/$', views.call_report, name='call_report'),
    url(r'^offer_parking/$', views.call_offer, name='call_offer'),
    url(r'^heatmap/$', views.call_heatmap, name='call_heatmap'),
    url(r'^history/$', views.call_history, name='call_history'),

    url(r'^offer_new_parking/$', views.offer_new_parking, name='offer_new_parking'),
    url(r'^report_free_parking/$', views.report_free_parking, name='report_free_parking'),

    url(r'^clear_msg/$', views.clear_msg, name='clear_msg'),

]

