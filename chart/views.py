import base64
import io
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'chart/index.html')


def inquiry(request):
    mpl.use('Agg')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([1, 2, 3, 4, 5, 6, 7, 8, 9])

    fig_file = io.BytesIO()
    fig.savefig(fig_file, format='png')
    b64 = base64.b64encode(fig_file.getvalue()).decode()

    context = {'graph': b64}

    return render(request, 'chart/chart.html', context)


def find_ticker(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({'tickers': ['APPL', 'AMZN']}), content_type='application/json')
