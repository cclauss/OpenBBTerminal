"""Chartexchange model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.op_helpers import convert

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_option_history(ticker: str, date: str, call: bool, price: str) -> pd.DataFrame:
    """Historic prices for a specific option [chartexchange]

    Parameters
    ----------
    ticker : str
        Ticker to get historical data from
    date : str
        Date as a string YYYYMMDD
    call : bool
        Whether to show a call or a put
    price : str
        Strike price for a specific option

    Returns
    -------
    historical : pd.Dataframe
        Historic information for an option
    """
    url = (
        f"https://chartexchange.com/symbol/opra-{ticker.lower()}{date.replace('-', '')}"
    )
    url += f"{'c' if call else 'p'}{float(price):g}/historical/"

    data = requests.get(url, headers={"User-Agent": get_user_agent()}).content
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("div", attrs={"style": "display: table; font-size: 0.9em; "})
    if table:
        rows = table.find_all("div", attrs={"style": "display: table-row;"})
    else:
        return pd.DataFrame()
    clean_rows = []

    if rows:
        for row in rows[1:]:
            item = row.find_all("div")
            clean_rows.append([x.text for x in item])
    else:
        console.print("No data for this option\n")
        return pd.DataFrame()

    df = pd.DataFrame()
    df["Date"] = [x[0] for x in clean_rows]
    df["Open"] = [convert(x[2], ",") for x in clean_rows]
    df["High"] = [convert(x[3], ",") for x in clean_rows]
    df["Low"] = [convert(x[4], ",") for x in clean_rows]
    df["Close"] = [convert(x[5], ",") for x in clean_rows]
    df["Change"] = [convert(x[6], "%") for x in clean_rows]
    df["Volume"] = [convert(x[7], ",") for x in clean_rows]
    df["Open Interest"] = [convert(x[8], ",") for x in clean_rows]
    df["Change Since"] = [convert(x[9], "%") for x in clean_rows]

    return df
