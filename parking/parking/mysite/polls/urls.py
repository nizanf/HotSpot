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
    url(r'^find_parking/$', views.call_find, name='call_find'),
    url(r'^heatmap/$', views.call_heatmap, name='call_heatmap'),
    url(r'^history/$', views.call_history, name='call_history'),
    url(r'^last_activity/$', views.call_last_activity, name='call_last_activity'),



    url(r'^offer_new_parking/$', views.offer_new_parking, name='offer_new_parking'),
    url(r'^report_free_parking/$', views.report_free_parking, name='report_free_parking'),
    url(r'^find_new_parking/$', views.find_new_parking, name='find_new_parking'),
  
    url(r'^update_spots_on_map/$', views.update_spots_on_map, name='update_spots_on_map'),

    url(r'^clear_msg/$', views.clear_msg, name='clear_msg'),

    url(r'^user_query/$', views.user_query, name='user_query'),

    url(r'^aut_pincode/$', views.aut_pincode, name='aut_pincode'),

    url(r'^seller_cancel_parking/$', views.seller_cancel_parking, name='seller_cancel_parking'),
    url(r'^buyer_cancel_parking/$', views.buyer_cancel_parking, name='buyer_cancel_parking'),

    url(r'^seller_report_parking/$', views.seller_report_parking, name='seller_report_parking'),
    url(r'^buyer_report_parking/$', views.buyer_report_parking, name='buyer_report_parking'),
]

