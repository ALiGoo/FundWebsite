import pandas as pd
import numpy as np

from django.http import JsonResponse
from django.shortcuts import redirect, render
from fundapp.profit_test import img
from datetime import datetime
from sqlalchemy import create_engine
from collections import defaultdict


def test(request):
    if request.method == "POST":
        url = "/test/start_year=" + request.POST['start_year'] + \
            " start_month=" + request.POST['start_month'] + \
            " end_year=" + request.POST['end_year'] + \
            " end_month=" + request.POST['end_month'] + \
            " investement_type=" + request.POST['investement_type'] + \
            " sharpe_ratio=" + request.POST['sharpe_ratio'] + \
            " std=" + request.POST['std'] + \
            " beta=" + request.POST['beta'] + \
            " treynor_ratio=" + request.POST['treynor_ratio'] + \
            " btest_time=" + request.POST['btest_time'] + \
            " money=" + request.POST['money'] + \
            " buy_ratio0=" + request.POST['buy_ratio0'] + \
            " buy_ratio1=" + request.POST['buy_ratio1'] + \
            " buy_ratio2=" + request.POST['buy_ratio2'] + \
            " buy_ratio3=" + request.POST['buy_ratio3'] + \
            " strategy=" + request.POST['strategy'] + \
            " frequency=" + request.POST['frequency'] + "/"
        return redirect(url)
    return render(request, "test.html", locals())


def test_show(request, start_year, start_month, end_year, end_month, investement_type, sharpe_ratio, std, beta, treynor_ratio, btest_time, money, buy_ratio0, buy_ratio1, buy_ratio2, buy_ratio3, strategy, frequency):
    return render(request, "test_show.html", locals())


def test_respoonse(request, start_year, start_month, end_year, end_month, investement_type, sharpe_ratio, std, beta, treynor_ratio, btest_time, money, buy_ratio0, buy_ratio1, buy_ratio2, buy_ratio3, strategy, frequency):
    response_data = img(start=datetime.strptime("-".join([start_year, start_month]), '%Y-%m'),
                        end=datetime.strptime("-".join([end_year, end_month]), '%Y-%m'),
                        investement_type=np.asarray(investement_type.split(" ")),
                        sharpe_ratio=sharpe_ratio,
                        std=std,
                        beta=beta,
                        treynor_ratio=treynor_ratio,
                        btest_time=btest_time,
                        money=money,
                        buy_ratio=np.asarray([float(buy_ratio0), float(buy_ratio1), float(buy_ratio2), float(buy_ratio3)], dtype=np.float),
                        strategy=strategy,
                        frequency=frequency)
    return JsonResponse(response_data)


def index(request):
    engine = create_engine('sqlite:///fund.db')
    items = pd.read_sql(
        sql='select * from basic_information limit 10', con=engine)
    items = items.to_dict('records', into=defaultdict(list))
    return render(request, "index.html", locals())

def index_response(request, page):
    engine = create_engine('sqlite:///fund.db')
    items = pd.read_sql(
        sql='select * from basic_information limit ?,10', con=engine, params=[(page-1)*10])
    items = items.to_dict('index')
    return JsonResponse(items)