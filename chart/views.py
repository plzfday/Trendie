import json

from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import TickerForm
from .graph import get_stock_data
from .models import Ticker


def index(request):
    return render(request, "chart/index.html")


def inquiry(request, ticker):
    duration = request.GET.get("duration", "5Y")

    if duration not in ["5Y", "1.5Y", "VS19", "9M"]:
        duration = "5Y"

    topics = list(Ticker.objects.filter(ticker__exact=ticker)
                  .values_list('keywords', flat=True))

    graphs, names = get_stock_data(ticker, duration, topics)
    context = {"graphs": zip(graphs, names)}

    return render(request, "chart/chart.html", context)


def keywords(request):
    if request.method == "POST":
        form = TickerForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("chart:index")
    else:
        return render(request, "chart/keyword.html")


def find_ticker(request):
    if request.method == "GET":
        tickers = Ticker.objects.all() \
            .values_list('ticker', flat=True) \
            .distinct()

        return HttpResponse(
            json.dumps({"tickers": list(tickers)}), content_type="application/json"
        )
