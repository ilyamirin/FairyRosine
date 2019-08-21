from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    url(r'^category/(?P<id>\d+)/$', views.category, name='category'),
    url(r'^coin/(?P<id>\d+)/$', views.coin, name='coin'),
    url(r'^stream/$', views.stream, name='stream'),
    url(r'^$', views.index, name='index'),
    url(r'^dialog/$', views.dialog, name='dialog'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)