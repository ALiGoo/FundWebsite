from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from fundapp.views import index, index_response, test, test_respoonse, search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index),
    path('index/p=<int:page>', index_response),
    path('index/c=<str:column>&key=<str:keyword>', search),
    path('test/', test),
    path('test/<str:start_year>&<str:start_month>&<str:end_year>&<str:end_month>&<str:investement_type>&<str:sharpe_ratio>&<str:std>&<str:beta>&<str:treynor_ratio>&<int:btest_time>&<int:money>&<str:buy_ratio0>&<str:buy_ratio1>&<str:buy_ratio2>&<str:buy_ratio3>&<int:strategy>&<int:frequency>/', test_respoonse),
]
