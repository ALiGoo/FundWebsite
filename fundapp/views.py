from django.http import JsonResponse
from django.shortcuts import redirect, render
from fundapp.profit_test import img
import numpy as np

mds_img = {}

def test(request):
    if request.method == "POST":
        start = "-".join([request.POST['start_year'],
                          request.POST['start_month']])
        end = "-".join([request.POST['end_year'], request.POST['end_month']])
        investement_type = request.POST['investement_type'].split(" ")
        sharpe_ratio = float(request.POST['sharpe_ratio'])
        std = float(request.POST['std'])
        beta = float(request.POST['beta'])
        treynor_ratio = float(request.POST['treynor_ratio'])
        money = int(request.POST['money'])
        buy_ratio = np.asarray((0,0,0,0), dtype=np.float)
        for i in range(4):
            buy_ratio[i] = float(request.POST['buy_ratio' + str(i)])
        strategy = request.POST['strategy']
        frequency = int(request.POST['frequency'])

        global mds_img
        profit_img, mds_img = img(start, end, investement_type, sharpe_ratio, std, beta, treynor_ratio, money, buy_ratio, strategy, frequency)
        return render(request, "test_show.html", {'profit_img':profit_img, 'mds_img':mds_img[start]})
    return render(request, "test.html", locals())


def mds(request, mds_img_idx):
    return JsonResponse(mds_img[mds_img_idx])
