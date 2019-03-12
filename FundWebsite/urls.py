from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from fundapp.views import index, test, test_respoonse, test_show

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test),
    path('index/', index),
    path('test/start_year=<str:start_year> start_month=<str:start_month> end_year=<str:end_year> end_month=<str:end_month> investement_type=<str:investement_type> sharpe_ratio=<str:sharpe_ratio> std=<str:std> beta=<str:beta> treynor_ratio=<str:treynor_ratio> btest_time=<int:btest_time> money=<int:money> buy_ratio0=<str:buy_ratio0> buy_ratio1=<str:buy_ratio1> buy_ratio2=<str:buy_ratio2> buy_ratio3=<str:buy_ratio3> strategy=<int:strategy> frequency=<int:frequency>/', test_show),
    path('test/start_year=<str:start_year> start_month=<str:start_month> end_year=<str:end_year> end_month=<str:end_month> investement_type=<str:investement_type> sharpe_ratio=<str:sharpe_ratio> std=<str:std> beta=<str:beta> treynor_ratio=<str:treynor_ratio> btest_time=<int:btest_time> money=<int:money> buy_ratio0=<str:buy_ratio0> buy_ratio1=<str:buy_ratio1> buy_ratio2=<str:buy_ratio2> buy_ratio3=<str:buy_ratio3> strategy=<int:strategy> frequency=<int:frequency>/response/', test_respoonse),
]
