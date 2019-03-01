from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from fundapp.views import mds, test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test),
    url(r'^ajax_list/(?P<mds_img_idx>\d{4}-\d{2})/$', mds),
]
