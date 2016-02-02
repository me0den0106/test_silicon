from django.conf.urls import url

from . import views

urlpatterns = [	
	url(r'^$', views.index, name='index'),
    # url(r'^(?P<errorMessage>.*)$', views.index, name='index_with_message'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^regist$', views.regist, name='regist'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^comment/(?P<img_id>[0-9]+)/$', views.comment, name='comment'),
    url(r'^search$', views.search, name='search'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^notification$', views.notification, name='notification'),
]