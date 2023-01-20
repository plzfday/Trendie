import base64
import io

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import yfinance as yf

from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

from .models import Company


class NoDataError(Exception):
    pass


def format_date(start, end):
    format = "%Y-%m-%d"
    return f"{start.strftime(format)} {end.strftime(format)}"


def fetch_stock_data_normalized(ticker, date_range):
    if ticker.endswith(".KS"):
        stock = web.DataReader(ticker[:-3], "naver", *date_range)
        stock = stock.iloc[:, -2].astype("int")
    else:
        yf.pdr_override()
        start, end = date_range
        stock = web.get_data_yahoo(ticker, start=start, end=end)
        stock = stock.iloc[:, -2]

    return (stock - stock.min()) / (stock.max() - stock.min()) * 100


def fetch_from_google_trend(date_range, topics, duration: str):
    pytrend = TrendReq(timeout=(10, 25))
    year_ahead = date_range[0] + relativedelta(years=-1)

    tf = format_date(year_ahead, date_range[1])

    yoy_offset = 52
    ma_offset = 10
    if duration == "5Y":
        yoy_offset = 12
        ma_offset = 2

    data = []

    for topic in topics:
        pytrend.build_payload([topic], timeframe=tf, geo='US')

        try:
            trend = handle_blank(pytrend.interest_over_time())
        except ResponseError:
            raise RuntimeError("Google returned 429")

        if trend.empty:
            raise NoDataError(
                f"Keyword <b>{topic}</b> doesn't have enough data. Use another keyword.")

        trend_ma = handle_blank(trend.rolling(window=ma_offset).mean())
        trend_ma_yoy = calc_yoy(trend_ma, yoy_offset - ma_offset + 1)

        data.append({"trend_ma_yoy": trend_ma_yoy.iloc[:, 0],
                     "trend_ma": trend_ma.iloc[yoy_offset - ma_offset + 1:, 0],
                     "trend": trend.iloc[yoy_offset:, 0]})

    return data


def get_graph(ticker, duration, topics):
    mpl.use("Agg")
    today = datetime.today()
    start = calc_start_date(today, duration)

    name = get_title(ticker)
    graphs, names = [], []

    stock = fetch_stock_data_normalized(ticker, (start, today))

    try:
        data = fetch_from_google_trend((start, today), topics, duration)
    except (ResponseError, NoDataError) as e:
        raise e

    for i in range(len(topics)):
        data[i].update({"stock": stock})
        graphs.append(plot(data[i]))
        names.append(f"{name} / {topics[i]}")

    return graphs, names


def handle_blank(data):
    return data.dropna().replace(0, 1)


def calc_yoy(data, offset):
    return (data - data.shift(offset)) / data.shift(offset) * 100


def get_title(ticker):
    company_name = Company.objects.get(ticker=ticker).name
    return f"{ticker} ({company_name})"


def calc_start_date(today, duration):
    start = None
    if duration == "5Y":
        start = today + relativedelta(years=-5)
    elif duration == "1.5Y":
        start = today + relativedelta(years=-1, months=-6)
    elif duration == "9M":
        start = today + relativedelta(months=-9)

    return start


def plot(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.autofmt_xdate(rotation=45)

    ax.plot(data["trend"].index, data["trend"], color="mediumslateblue")
    ax.plot(data["trend_ma"].index, data["trend_ma"], color="red")
    ax.plot(data["stock"].index, data["stock"], color="black")

    ax.set_ylim(0, 100)
    ax.grid(axis='both')

    ax2 = ax.twinx()
    ax2.plot(data["trend_ma_yoy"].index, data["trend_ma_yoy"], color="gold")

    ylim_low = data["trend_ma_yoy"].min()
    ylim_hi = data["trend_ma_yoy"].max()
    ax2.set_ylim(ylim_low, ylim_hi)
    plt.tight_layout()

    fig_file = io.BytesIO()
    fig.savefig(fig_file, format="png")

    graph = base64.b64encode(fig_file.getvalue()).decode()

    return graph
