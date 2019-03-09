from django.http import JsonResponse
from django.shortcuts import redirect, render
from fundapp.profit_test import img
import numpy as np
from datetime import datetime

mds_img = {}


def test(request):
    if request.method == "POST":
        start = datetime.strptime(
            "-".join([request.POST['start_year'], request.POST['start_month']]), '%Y-%m')
        end = datetime.strptime(
            "-".join([request.POST['end_year'], request.POST['end_month']]), '%Y-%m')
        investement_type = np.asarray(request.POST['investement_type'].split(" "))
        sharpe_ratio = request.POST['sharpe_ratio']
        std = request.POST['std']
        beta = request.POST['beta']
        treynor_ratio = request.POST['treynor_ratio']
        btest_time = int(request.POST['btest_time'])
        money = int(request.POST['money'])
        buy_ratio = np.asarray((0, 0, 0, 0), dtype=np.float)
        # for i in range(4):
        #     buy_ratio[i] = float(request.POST['buy_ratio' + str(i)])
        buy_ratio = np.asarray([float(request.POST['buy_ratio' + str(i)]) for i in range(4)], dtype=np.float)
        strategy = int(request.POST['strategy'])
        frequency = int(request.POST['frequency'])

        global mds_img
        profit_img, mds_img, profit_indicator = img(start, end, investement_type, sharpe_ratio,
                                                    std, beta, treynor_ratio, btest_time, money, buy_ratio, strategy, frequency)
        return render(request, "test_show.html", {'profit_img': profit_img,
                                                  'mds_img': mds_img[start.strftime('%Y-%m')],
                                                  'profit_indicator': profit_indicator})
    return render(request, "test.html", locals())


def mds(request, mds_img_idx):
    return JsonResponse(mds_img[mds_img_idx])
