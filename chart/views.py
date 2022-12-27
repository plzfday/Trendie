import json
import urllib

from django.http import HttpResponse
from django.shortcuts import render, redirect

from .graph import get_stock_data
from .models import Company


def index(request):
    return render(request, "chart/index.html")


def inquiry(request, ticker):
    DEFAULT_DURATION = "5Y"
    duration = request.GET.get("duration", DEFAULT_DURATION)

    topics = list(Company.objects.get(
        ticker=ticker).keyword_set.values_list('keyword', flat=True))

    graphs, names = get_stock_data(ticker, duration, topics)
    context = {"graphs": zip(graphs, names)}

    return render(request, "chart/chart.html", context)


def fetch_name_from_ticker(ticker):
    # get company name from ticker
    payload = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
    response = urllib.request.urlopen(payload)
    content = response.read()
    data = json.loads(content.decode("utf8"))["quotes"][0]["shortname"]

    return data


def keywords(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker")
        kws = request.POST.getlist("keywords")

        name = fetch_name_from_ticker(ticker)
        company, created = Company.objects.get_or_create(
            ticker=ticker, name=name)
        for keyword in kws:
            company.keyword_set.create(keyword=keyword)
        return redirect("chart:index")
    else:
        tickers = get_all_tickers()
        context = {"tickers": tickers}
        return render(request, "chart/keyword.html", context)


def keywords_edit(request):
    ticker = request.POST.get("ticker")
    kws = Company.objects.get(ticker=ticker) \
        .keyword_set.values_list("keyword", flat=True)
    context = {"ticker": ticker, "keywords": kws}
    return render(request, "chart/keywords_edit.html", context)


def keywords_edit_complete(request):
    ticker = request.POST.get("ticker")
    kws = request.POST.getlist("keywords")

    company = Company.objects.get(ticker=ticker)
    company.keyword_set.all().delete()
    for kw in kws:
        company.keyword_set.create(keyword=kw)
    return redirect("chart:index")


def find_ticker(request):
    if request.method == "GET":
        tickers = get_all_tickers()

        return HttpResponse(
            json.dumps({"tickers": list(tickers)}), content_type="application/json"
        )


def get_all_tickers():
    return Company.objects.values_list("ticker", flat=True)


def page_not_found(request, exception):
    return render(request, "chart/404.html", {})
