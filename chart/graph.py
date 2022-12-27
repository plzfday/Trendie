import base64
import datetime
import io
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
from pytrends.request import TrendReq

from .models import Company


def get_stock_data(ticker, duration, topics):
    mpl.use("Agg")
    today = datetime.date.today()
    start = calc_start_date(today, duration)
    yearforyoy = start + relativedelta(years=-1)

    stock = web.DataReader(ticker, "yahoo", start, today)
    stock = (stock - stock.min()) / (stock.max() - stock.min()) * 100

    graphs = list()
    names = list()
    pytrend = TrendReq(timeout=(10, 25))
    name = get_title(ticker)
    kw_list = topics
    tf = start.strftime("%Y-%m-%d") + " " + today.strftime("%Y-%m-%d")
    tf_yoy = yearforyoy.strftime("%Y-%m-%d") + " " + start.strftime("%Y-%m-%d")

    for i in range(len(kw_list)):
        pytrend.build_payload([kw_list[i]], timeframe=tf, geo='US')

        trend = pytrend.interest_over_time().drop(columns=['isPartial'])
        trend = handle_blank(trend)

        pytrend.build_payload([kw_list[i]], timeframe=tf_yoy, geo='US')
        trend_yoy = pytrend.interest_over_time().drop(columns=['isPartial'])
        trend_yoy = pd.concat([trend_yoy, trend])
        yoy_ma = trend_yoy.rolling(window=10).mean()
        yoy_ma = handle_blank(yoy_ma)
        trend_ma_yoy = calc_yoy(yoy_ma)

        trend_ma = trend.rolling(window=10).mean()
        trend_ma = handle_blank(trend_ma)

        data = {"record": stock.iloc[:, -1],
                "trend_ma_yoy": trend_ma_yoy.iloc[:, 0],
                "trend_ma": trend_ma.iloc[:, 0],
                "trend": trend.iloc[:, 0]}

        graphs.append(plot(data))
        names.append(f"{name} / {kw_list[i]}")

    return graphs, names


def handle_blank(data):
    return data.dropna().replace(0, 1)


def calc_yoy(data):
    return (data - data.shift(52)) / data.shift(52) * 100


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
    ax.plot(data["record"].index, data["record"], color="black")

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
