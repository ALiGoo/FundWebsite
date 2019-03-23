import pandas as pd
import numpy as np

from django.http import JsonResponse
from django.shortcuts import redirect, render
from fundapp.profit_test import img
from datetime import datetime
from sqlalchemy import create_engine
from collections import defaultdict

engine = create_engine('sqlite:///fund.db')


def test(request):
    if request.method == "POST":
        url = "/test/" + "-".join([request.POST['start_year'], request.POST['start_month']]) + \
            "&" + "-".join([request.POST['end_year'], request.POST['end_month']]) + \
            "&" + request.POST['investement_type'] + \
            "& " + request.POST['sharpe_ratio'] + \
            "& " + request.POST['std'] + \
            "& " + request.POST['beta'] + \
            "& " + request.POST['treynor_ratio'] + \
            "&" + request.POST['btest_time'] + \
            "&" + request.POST['money'] + \
            "&" + request.POST['buy_ratio0'] + \
            "," + request.POST['buy_ratio1'] + \
            "," + request.POST['buy_ratio2'] + \
            "," + request.POST['buy_ratio3'] + \
            "&" + request.POST['strategy'] + \
            "&" + request.POST['frequency'] + "/"
        return render(request, "test_show.html", locals())
    return render(request, "test.html", locals())


def test_respoonse(request, start, end, investement_type, sharpe_ratio, std, beta, treynor_ratio, btest_time, money, buy_ratio, strategy, frequency):
    response_data = img(start=datetime.strptime(start, '%Y-%m'),
                        end=datetime.strptime(end, '%Y-%m'),
                        investement_type=np.asarray(
                        investement_type.split(" ")),
                        sharpe_ratio=sharpe_ratio,
                        std=std,
                        beta=beta,
                        treynor_ratio=treynor_ratio,
                        btest_time=btest_time,
                        money=money,
                        buy_ratio = np.asarray(buy_ratio.split(","), dtype=np.float),
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
    items = pd.read_sql(
        sql='select * from basic_information limit ?,10', con=engine, params=[(page-1)*10])
    items = items.to_dict('index')
    return JsonResponse(items)


def search(request, column, keyword):
    items = pd.read_sql(sql='select * from basic_information', con=engine)
    if "fee" in column:
        items = items[items[column] <= float(keyword)]
    else:
        items = items[items[column].str.contains(keyword)]
    items = items.to_dict('index')
    return JsonResponse(items)
