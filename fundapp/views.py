import pandas as pd
import numpy as np

from django.http import JsonResponse
from django.shortcuts import redirect, render
from fundapp.profit_test import img
from datetime import datetime
from sqlalchemy import create_engine
from collections import OrderedDict, defaultdict

response_data = {}

def test(request):
    if request.method == "POST":
        global response_data
        # profit_img, mds_img, profit_indicator, mean_similarity = img(start=datetime.strptime("-".join([request.POST['start_year'], request.POST['start_month']]), '%Y-%m'),
        #                                                              end=datetime.strptime(
        #                                                                  "-".join([request.POST['end_year'], request.POST['end_month']]), '%Y-%m'),
        #                                                              investement_type=np.asarray(
        #                                                                  request.POST['investement_type'].split(" ")),
        #                                                              sharpe_ratio=request.POST['sharpe_ratio'],
        #                                                              std=request.POST['std'],
        #                                                              beta=request.POST['beta'],
        #                                                              treynor_ratio=request.POST['treynor_ratio'],
        #                                                              btest_time=int(
        #                                                                  request.POST['btest_time']),
        #                                                              money=int(
        #                                                                  request.POST['money']),
        #                                                              buy_ratio=np.asarray(
        #     [float(request.POST['buy_ratio' + str(i)]) for i in range(4)], dtype=np.float),
        #     strategy=int(request.POST['strategy']),
        #     frequency=int(request.POST['frequency'])
        # )

        response_data = img(start=datetime.strptime("-".join([request.POST['start_year'], request.POST['start_month']]), '%Y-%m'),
                            end=datetime.strptime("-".join([request.POST['end_year'], request.POST['end_month']]), '%Y-%m'),
                            investement_type=np.asarray(request.POST['investement_type'].split(" ")),
                            sharpe_ratio=request.POST['sharpe_ratio'],
                            std=request.POST['std'],
                            beta=request.POST['beta'],
                            treynor_ratio=request.POST['treynor_ratio'],
                            btest_time=int(request.POST['btest_time']),
                            money=int(request.POST['money']),
                            buy_ratio=np.asarray([float(request.POST['buy_ratio' + str(i)]) for i in range(4)], dtype=np.float),
                            strategy=int(request.POST['strategy']),
                            frequency=int(request.POST['frequency'])
        )

        # return render(request, "test_show.html", {'profit_img': profit_img,
        #                                           'mds_img': mds_img["-".join([request.POST['start_year'], request.POST['start_month']])],
        #                                           'profit_indicator': profit_indicator,
        #                                           'mean_similarity': mean_similarity})
        return render(request, "test_show.html",{'response_data':response_data})
    return render(request, "test.html", locals())


def mds(request):
    global response_data
    return JsonResponse(response_data)


def index(request):
    engine = create_engine('sqlite:///fund.db')
    items = pd.read_sql(
        sql='select * from basic_information', con=engine)
    items = items.to_dict('records', into=defaultdict(list))
    return render(request, "index.html", locals())
