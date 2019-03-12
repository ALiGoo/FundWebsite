from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from fundapp.views import mds, test, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test),
    path('mds_img/', mds),
    path('index/', index),
]
