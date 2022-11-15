import json

from django.http import HttpResponse
from django.shortcuts import render, redirect

from .graph import get_stock_data
from .models import Ticker


def index(request):
    return render(request, "chart/index.html")


def inquiry(request, ticker):
    duration = request.GET.get("duration", "5Y")

    if duration not in ["5Y", "1.5Y", "VS19", "9M"]:
        duration = "5Y"

    topics = list(Ticker.objects.filter(ticker__exact=ticker)
                  .values_list('keyword', flat=True))

    graphs, names = get_stock_data(ticker, duration, topics)
    context = {"graphs": zip(graphs, names)}

    return render(request, "chart/chart.html", context)


def keywords(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker")
        kws = request.POST.getlist("keywords")
        for keyword in kws:
            Ticker(ticker=ticker, keyword=keyword).save()
        return redirect("chart:index")
    else:
        tickers = Ticker.objects.values_list("ticker", flat=True).distinct()
        context = {"tickers": tickers}
        return render(request, "chart/keyword.html", context)


def keywords_edit(request):
    ticker = request.POST.get("ticker")
    kws = Ticker.objects.filter(ticker=ticker).values_list("keyword", flat=True)
    context = {"ticker": ticker, "keywords": kws}
    return render(request, "chart/keywords_edit.html", context)


def keywords_edit_complete(request):
    ticker = request.POST.get("ticker")
    kws = request.POST.getlist("keywords")
    print(ticker)
    Ticker.objects.filter(ticker=ticker).delete()
    for kw in kws:
        Ticker(ticker=ticker, keyword=kw).save()
    return redirect("chart:index")


def find_ticker(request):
    if request.method == "GET":
        tickers = Ticker.objects.all() \
            .values_list('ticker', flat=True) \
            .distinct()

        return HttpResponse(
            json.dumps({"tickers": list(tickers)}), content_type="application/json"
        )
