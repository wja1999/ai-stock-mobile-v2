import os
import re
import html as html_lib
import xml.etree.ElementTree as ET
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from openai import OpenAI
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =====================================================
# DeepSeek Key 配置
# Streamlit Cloud 推荐在 Secrets 里配置：
# DEEPSEEK_API_KEY = "你的DeepSeek Key"
# =====================================================
DEEPSEEK_API_KEY = "sk-34bde63deba4488c939677b2a93fbb01"

try:
    if DEEPSEEK_API_KEY == "这里填你的DeepSeek key":
        DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
except Exception:
    pass

client = OpenAI(
    api_key=DEEPSEEK_API_KEY if DEEPSEEK_API_KEY else "EMPTY",
    base_url="https://api.deepseek.com"
)


# =====================================================
# 页面基础配置：手机端
# =====================================================
st.set_page_config(
    page_title="AI股票分析平台",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =====================================================
# 手机端 UI 样式
# =====================================================
st.markdown(
    """
<style>
:root {
    --bg: #f7f8fb;
    --card: #ffffff;
    --text: #111827;
    --muted: #6b7280;
    --red: #ef4444;
    --green: #16a34a;
    --blue: #2563eb;
    --orange: #f97316;
    --border: #edf0f5;
    --shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(239,68,68,.10), transparent 28%),
        radial-gradient(circle at 90% 8%, rgba(37,99,235,.10), transparent 30%),
        linear-gradient(180deg, #fff7f4 0%, #f7f8fb 36%, #ffffff 100%);
    color: var(--text);
}

.block-container {
    max-width: 430px !important;
    padding: 16px 14px 92px !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

h1, h2, h3, h4, h5, h6, p, li, span, div {
    color: var(--text);
}

.hero {
    background: linear-gradient(135deg, #fff2ed 0%, #ffffff 100%);
    border: 1px solid rgba(239,68,68,.14);
    border-radius: 24px;
    padding: 20px 18px;
    box-shadow: var(--shadow);
    margin-bottom: 14px;
}

.hero-title {
    font-size: 25px;
    font-weight: 900;
    line-height: 1.25;
    color: #111827;
}

.hero-sub {
    margin-top: 8px;
    color: #6b7280;
    font-size: 13px;
    line-height: 1.55;
    font-weight: 650;
}

.tag {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
    margin-right: 5px;
    margin-top: 10px;
    background: #fff1ed;
    color: #dc2626;
}

.card {
    background: rgba(255,255,255,.94);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 15px;
    margin-top: 13px;
    box-shadow: var(--shadow);
}

.section-title {
    font-size: 18px;
    font-weight: 900;
    margin: 2px 0 12px;
    color: #111827;
}

.tip {
    background: linear-gradient(90deg, rgba(239,68,68,.08), rgba(249,115,22,.08));
    border: 1px solid rgba(239,68,68,.12);
    border-radius: 16px;
    padding: 13px;
    color: #7f1d1d;
    font-size: 13px;
    line-height: 1.65;
    font-weight: 700;
}

.stTextInput label, .stSelectbox label {
    color: #374151 !important;
    font-weight: 800 !important;
    font-size: 13px !important;
}

.stTextInput input {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    height: 46px !important;
    font-weight: 750 !important;
    font-size: 15px !important;
}

.stTextInput input::placeholder {
    color: #9ca3af !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    min-height: 46px !important;
    font-weight: 750 !important;
    font-size: 15px !important;
}

.stButton button {
    width: 100%;
    height: 50px;
    border-radius: 999px;
    border: none;
    background: linear-gradient(90deg, #ef4444, #f97316);
    color: white !important;
    font-weight: 900;
    font-size: 16px;
    box-shadow: 0 14px 28px rgba(239,68,68,.22);
}

.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #edf0f5;
    border-radius: 16px;
    padding: 13px 10px;
    box-shadow: 0 8px 18px rgba(15,23,42,.05);
    min-height: 86px;
}

.metric-label {
    color: #6b7280;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 7px;
}

.metric-value {
    color: #111827;
    font-size: 22px;
    font-weight: 900;
    line-height: 1.15;
    word-break: break-all;
}

.metric-sub {
    color: #9ca3af;
    font-size: 11px;
    font-weight: 650;
    margin-top: 6px;
    line-height: 1.35;
}

.score-box {
    background: linear-gradient(135deg, #fff7f4, #ffffff);
    border: 1px solid rgba(239,68,68,.14);
    border-radius: 20px;
    padding: 16px;
}

.score-num {
    font-size: 44px;
    font-weight: 950;
    color: #ef4444;
    line-height: 1;
}

.score-total {
    color: #9ca3af;
    font-size: 18px;
    font-weight: 800;
}

.score-title {
    font-size: 18px;
    font-weight: 900;
    color: #111827;
    margin-top: 10px;
}

.score-desc {
    color: #4b5563;
    font-size: 13px;
    font-weight: 650;
    line-height: 1.6;
    margin-top: 6px;
}

.progress-bg {
    height: 10px;
    border-radius: 999px;
    background: #fee2e2;
    overflow: hidden;
    margin-top: 13px;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #ef4444, #f97316);
}

.decision-card {
    background: #ffffff;
    border: 1px solid #edf0f5;
    border-radius: 17px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 8px 18px rgba(15,23,42,.05);
}

.decision-title {
    font-size: 15px;
    font-weight: 900;
    margin-bottom: 7px;
}

.decision-price {
    font-size: 20px;
    font-weight: 950;
    color: #ef4444;
    margin-bottom: 7px;
}

.decision-text {
    color: #4b5563;
    font-size: 13px;
    line-height: 1.65;
    font-weight: 650;
}

.news-item {
    background: #ffffff;
    border: 1px solid #edf0f5;
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 9px;
}

.news-item a {
    color: #2563eb !important;
    font-size: 13px;
    line-height: 1.5;
    font-weight: 800;
    text-decoration: none;
}

.news-meta {
    color: #9ca3af;
    font-size: 11px;
    font-weight: 650;
    margin-top: 6px;
}

.ai-box {
    background: #ffffff;
    border: 1px solid #edf0f5;
    border-radius: 18px;
    padding: 15px;
    box-shadow: 0 8px 18px rgba(15,23,42,.05);
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #1f2937 !important;
    font-size: 14px;
    line-height: 1.75;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #111827 !important;
    font-weight: 900 !important;
    font-size: 18px !important;
    margin-top: 16px !important;
}

.bottom-safe {
    height: 18px;
}
</style>
""",
    unsafe_allow_html=True
)


# =====================================================
# 工具函数
# =====================================================
def is_valid_key() -> bool:
    if not DEEPSEEK_API_KEY:
        return False
    if DEEPSEEK_API_KEY == "这里填你的DeepSeek key":
        return False
    if DEEPSEEK_API_KEY == "EMPTY":
        return False
    return True


def safe_float(value, default=0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def format_price(value) -> str:
    value = safe_float(value)
    return f"{value:.2f}"


def format_big_number(value) -> str:
    value = safe_float(value)
    if abs(value) >= 100000000:
        return f"{value / 100000000:.2f}亿"
    if abs(value) >= 10000:
        return f"{value / 10000:.2f}万"
    return f"{value:.0f}"


def normalize_ticker(raw: str) -> str:
    code = str(raw).strip().upper()
    code = code.replace(" ", "")

    if not code:
        return "AAPL"

    if code.endswith(".SH"):
        code = code.replace(".SH", ".SS")

    if code.endswith(".SS") or code.endswith(".SZ") or code.endswith(".HK"):
        return code

    if re.fullmatch(r"\d{6}", code):
        if code.startswith(("6", "9")):
            return f"{code}.SS"
        return f"{code}.SZ"

    return code


def short_code(ticker: str) -> str:
    return ticker.replace(".SS", "").replace(".SZ", "").replace(".HK", "")


def is_a_share(ticker: str) -> bool:
    return ticker.endswith(".SS") or ticker.endswith(".SZ")


def get_market_colors(ticker: str):
    if is_a_share(ticker):
        return "#ef4444", "#16a34a"
    return "#16a34a", "#ef4444"


def flatten_columns(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    if isinstance(data.columns, pd.MultiIndex):
        new_cols = []
        for col in data.columns:
            picked = None
            for part in col:
                part_str = str(part)
                if part_str in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
                    picked = part_str
                    break
            if picked is None:
                picked = str(col[0])
            new_cols.append(picked)
        data.columns = new_cols
    else:
        data.columns = [str(col) for col in data.columns]

    rename_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adj close": "adj_close",
        "volume": "volume",
    }

    data.rename(columns=rename_map, inplace=True)
    data = data.loc[:, ~data.columns.duplicated()].copy()

    for col in ["open", "high", "low", "close", "volume"]:
        if col not in data.columns:
            data[col] = 0
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["open", "high", "low", "close"])
    return data[["open", "high", "low", "close", "volume"]].copy()


def fetch_price_data(ticker: str, period: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        period=period,
        auto_adjust=False,
        progress=False,
        threads=False,
        group_by="column"
    )

    if data is None or data.empty:
        return pd.DataFrame()

    data = flatten_columns(data)

    if data.empty:
        return pd.DataFrame()

    return data


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    df["ma5"] = df["close"].rolling(5, min_periods=1).mean()
    df["ma10"] = df["close"].rolling(10, min_periods=1).mean()
    df["ma20"] = df["close"].rolling(20, min_periods=1).mean()
    df["ma60"] = df["close"].rolling(60, min_periods=1).mean()

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd_dif"] = ema12 - ema26
    df["macd_dea"] = df["macd_dif"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = (df["macd_dif"] - df["macd_dea"]) * 2

    low_min = df["low"].rolling(9, min_periods=1).min()
    high_max = df["high"].rolling(9, min_periods=1).max()
    spread = (high_max - low_min).replace(0, np.nan)

    rsv = ((df["close"] - low_min) / spread * 100).fillna(50)
    df["kdj_k"] = rsv.ewm(com=2, adjust=False).mean()
    df["kdj_d"] = df["kdj_k"].ewm(com=2, adjust=False).mean()
    df["kdj_j"] = 3 * df["kdj_k"] - 2 * df["kdj_d"]

    df["volume_ma5"] = df["volume"].rolling(5, min_periods=1).mean()
    df["pct_change"] = df["close"].pct_change()

    return df


def fetch_news(ticker: str, stock_name: str, max_items: int = 5):
    query_words = []
    code = short_code(ticker)

    if stock_name.strip():
        query_words.append(stock_name.strip())

    query_words.append(code)

    if is_a_share(ticker):
        query = f'{" ".join(query_words)} 股票 财经 业绩 资金'
        hl = "zh-CN"
        gl = "CN"
        ceid = "CN:zh-Hans"
    else:
        query = f'{" ".join(query_words)} stock earnings finance news'
        hl = "zh-CN"
        gl = "CN"
        ceid = "CN:zh-Hans"

    url = f"https://news.google.com/rss/search?q={quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
    items = []

    try:
        resp = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

        root = ET.fromstring(resp.content)

        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            pub_date = item.findtext("pubDate") or ""
            source_node = item.find("source")
            source = source_node.text if source_node is not None else "新闻源"

            title = re.sub(r"\s+-\s+[^-]+$", "", title).strip()

            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "source": source,
                    "date": pub_date
                })

    except Exception:
        pass

    return items


def score_news(news_items):
    positive_words = [
        "增长", "盈利", "利好", "中标", "回购", "增持", "突破", "创新高",
        "上调", "买入", "净利", "业绩预增", "合作", "获批", "订单"
    ]
    negative_words = [
        "减持", "亏损", "下滑", "处罚", "风险", "诉讼", "问询", "退市",
        "立案", "违规", "暴跌", "预亏", "警示", "债务"
    ]

    pos = 0
    neg = 0

    for item in news_items:
        title = item.get("title", "")
        if any(word in title for word in positive_words):
            pos += 1
        if any(word in title for word in negative_words):
            neg += 1

    score = 8 + min(pos * 2, 6) - min(neg * 3, 8)
    return max(0, min(15, score)), pos, neg


def calculate_score(df: pd.DataFrame, risk: str, news_items):
    latest = df.iloc[-1]

    close = safe_float(latest["close"])
    open_price = safe_float(latest["open"])
    ma5 = safe_float(latest["ma5"])
    ma10 = safe_float(latest["ma10"])
    ma20 = safe_float(latest["ma20"])
    ma60 = safe_float(latest["ma60"])
    macd_dif = safe_float(latest["macd_dif"])
    macd_dea = safe_float(latest["macd_dea"])
    macd_hist = safe_float(latest["macd_hist"])
    kdj_j = safe_float(latest["kdj_j"])
    volume = safe_float(latest["volume"])
    volume_ma5 = safe_float(latest["volume_ma5"])

    trend_score = 0
    if close >= ma5:
        trend_score += 6
    if close >= ma10:
        trend_score += 6
    if close >= ma20:
        trend_score += 6
    if ma5 >= ma10:
        trend_score += 6
    if ma10 >= ma20:
        trend_score += 6

    momentum_score = 0
    if macd_dif >= macd_dea:
        momentum_score += 7
    if macd_hist >= 0:
        momentum_score += 5
    if 45 <= kdj_j <= 85:
        momentum_score += 6
    elif 20 <= kdj_j < 45:
        momentum_score += 4
    elif kdj_j > 85:
        momentum_score += 2
    if close >= open_price:
        momentum_score += 2
    momentum_score = min(20, momentum_score)

    volume_score = 8
    if volume > 0 and volume_ma5 > 0:
        volume_ratio = volume / volume_ma5
        if volume_ratio >= 1.3 and close >= open_price:
            volume_score = 18
        elif volume_ratio >= 1.05 and close >= open_price:
            volume_score = 15
        elif volume_ratio >= 1.3 and close < open_price:
            volume_score = 7
        elif volume_ratio < 0.75:
            volume_score = 6
        else:
            volume_score = 10

    recent = df.tail(20).copy()
    ret = recent["close"].pct_change().dropna()
    volatility = safe_float(ret.std())
    recent_high = safe_float(recent["high"].max())
    recent_low = safe_float(recent["low"].min())

    drawdown = 0
    if recent_high > 0:
        drawdown = (close - recent_high) / recent_high

    risk_score = 15
    if volatility > 0.045:
        risk_score -= 5
    elif volatility > 0.03:
        risk_score -= 3

    if drawdown < -0.12:
        risk_score -= 5
    elif drawdown < -0.07:
        risk_score -= 3

    if kdj_j > 100:
        risk_score -= 3

    risk_score = max(0, min(15, risk_score))

    news_score, news_pos, news_neg = score_news(news_items)

    total = int(round(trend_score + momentum_score + volume_score + risk_score + news_score))
    total = max(0, min(100, total))

    if total >= 80:
        level = "强势区"
        action = "趋势跟踪"
        action_desc = "适合已有仓位继续观察，新增仓位更适合等回踩。"
    elif total >= 65:
        level = "偏强区"
        action = "小仓试探"
        action_desc = "可以关注回踩低吸或突破确认，但需要设置止损线。"
    elif total >= 50:
        level = "中性区"
        action = "观察为主"
        action_desc = "多空没有明显胜负，适合等待放量突破或回踩企稳。"
    else:
        level = "风险区"
        action = "谨慎回避"
        action_desc = "短线结构偏弱，除非出现明显放量修复，否则不宜急于进场。"

    if risk == "低" and total < 70:
        action = "观察为主"
        action_desc = "你的风险偏好较低，当前分数不足以支持激进操作。"
    elif risk == "高" and 55 <= total < 70:
        action = "小仓试探"
        action_desc = "高风险偏好可以小仓观察，但必须严格设置止损。"

    return {
        "total": total,
        "level": level,
        "action": action,
        "action_desc": action_desc,
        "trend_score": int(trend_score),
        "momentum_score": int(momentum_score),
        "volume_score": int(volume_score),
        "risk_score": int(risk_score),
        "news_score": int(news_score),
        "news_pos": news_pos,
        "news_neg": news_neg,
        "latest_close": close,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "ma60": ma60,
        "macd_dif": macd_dif,
        "macd_dea": macd_dea,
        "macd_hist": macd_hist,
        "kdj_j": kdj_j,
        "volume": volume,
        "volume_ma5": volume_ma5,
        "recent_high": recent_high,
        "recent_low": recent_low,
        "volatility": volatility,
        "drawdown": drawdown,
    }


def calculate_trade_map(df: pd.DataFrame, score_info: dict):
    latest = df.iloc[-1]

    close = safe_float(latest["close"])
    ma5 = safe_float(latest["ma5"])
    ma10 = safe_float(latest["ma10"])
    ma20 = safe_float(latest["ma20"])

    recent = df.tail(20)
    recent_high = safe_float(recent["high"].max())
    recent_low = safe_float(recent["low"].min())

    support_main = min(ma5, ma10, ma20)
    support_high = max(ma5, ma10, ma20)

    if support_main <= 0:
        support_main = recent_low

    watch_low = min(support_main, close)
    watch_high = max(support_high, close)

    breakout = recent_high
    stop_loss = min(recent_low, close * 0.95)

    return {
        "watch_low": watch_low,
        "watch_high": watch_high,
        "breakout": breakout,
        "stop_loss": stop_loss,
        "support_main": support_main,
        "recent_high": recent_high,
        "recent_low": recent_low,
    }


def build_kline_chart(df: pd.DataFrame, ticker: str):
    up_color, down_color = get_market_colors(ticker)

    plot_df = df.copy().reset_index()
    date_col = plot_df.columns[0]
    plot_df["date_label"] = pd.to_datetime(plot_df[date_col]).dt.strftime("%m-%d")
    plot_df["x"] = list(range(len(plot_df)))

    volume_colors = [
        up_color if safe_float(row["close"]) >= safe_float(row["open"]) else down_color
        for _, row in plot_df.iterrows()
    ]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(
        go.Candlestick(
            x=plot_df["x"],
            open=plot_df["open"],
            high=plot_df["high"],
            low=plot_df["low"],
            close=plot_df["close"],
            increasing_line_color=up_color,
            increasing_fillcolor=up_color,
            decreasing_line_color=down_color,
            decreasing_fillcolor=down_color,
            name="K线"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=plot_df["x"],
            y=plot_df["volume"],
            marker_color=volume_colors,
            opacity=0.55,
            name="成交量"
        ),
        row=2,
        col=1
    )

    step = max(1, len(plot_df) // 5)
    tick_vals = plot_df["x"][::step]
    tick_text = plot_df["date_label"][::step]

    fig.update_xaxes(
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_text,
        showgrid=False,
        zeroline=False,
        rangeslider_visible=False,
        row=1,
        col=1
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_text,
        showgrid=False,
        zeroline=False,
        row=2,
        col=1
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False,
        title_text="",
        row=1,
        col=1
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        title_text="",
        row=2,
        col=1
    )

    fig.update_layout(
        height=315,
        margin=dict(l=4, r=4, t=4, b=4),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.25)",
        font=dict(color="#374151", size=10),
        xaxis_rangeslider_visible=False
    )

    return fig


def metric_card(label, value, sub=""):
    return f"""
<div class="metric-card">
    <div class="metric-label">{html_lib.escape(str(label))}</div>
    <div class="metric-value">{html_lib.escape(str(value))}</div>
    <div class="metric-sub">{html_lib.escape(str(sub))}</div>
</div>
"""


def decision_card(title, price, text):
    st.markdown(
        f"""
<div class="decision-card">
    <div class="decision-title">{html_lib.escape(title)}</div>
    <div class="decision-price">{html_lib.escape(price)}</div>
    <div class="decision-text">{html_lib.escape(text)}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_score(score_info):
    total = score_info["total"]
    width = max(0, min(100, total))

    st.markdown(
        f"""
<div class="score-box">
    <div style="color:#6b7280;font-size:12px;font-weight:850;margin-bottom:8px;">AI综合评分</div>
    <span class="score-num">{total}</span>
    <span class="score-total">/100</span>
    <div class="score-title">{html_lib.escape(score_info["level"])} · {html_lib.escape(score_info["action"])}</div>
    <div class="score-desc">{html_lib.escape(score_info["action_desc"])}</div>
    <div class="progress-bg">
        <div class="progress-fill" style="width:{width}%;"></div>
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
<div class="metric-grid" style="margin-top:10px;">
    {metric_card("趋势结构", f'{score_info["trend_score"]}/30', "均线方向")}
    {metric_card("动能指标", f'{score_info["momentum_score"]}/20', "MACD / KDJ")}
    {metric_card("成交量资金", f'{score_info["volume_score"]}/20', "量价配合")}
    {metric_card("风险状态", f'{score_info["risk_score"]}/15', "波动与回撤")}
    {metric_card("消息面", f'{score_info["news_score"]}/15', f'利好{score_info["news_pos"]} 风险{score_info["news_neg"]}')}
    {metric_card("最新价", format_price(score_info["latest_close"]), "最新收盘价")}
</div>
""",
        unsafe_allow_html=True
    )


def render_news(news_items):
    st.markdown('<div class="section-title">📰 个股消息面</div>', unsafe_allow_html=True)

    if not news_items:
        st.markdown(
            """
<div class="tip">暂未抓取到高相关个股新闻，当前分析主要参考K线、成交量、技术指标与AI解读。</div>
""",
            unsafe_allow_html=True
        )
        return

    for item in news_items:
        title = html_lib.escape(item.get("title", ""))
        link = item.get("link", "")
        source = html_lib.escape(item.get("source", "新闻源"))
        st.markdown(
            f"""
<div class="news-item">
    <a href="{link}" target="_blank">{title}</a>
    <div class="news-meta">{source}</div>
</div>
""",
            unsafe_allow_html=True
        )


def fallback_analysis(ticker, stock_name, score_info, trade_map):
    name_part = f"{stock_name}（{ticker}）" if stock_name else ticker

    return f"""
### 一、先给小白看的结论

1. 当前 {name_part} 的 AI 综合评分为 **{score_info["total"]}/100**，属于 **{score_info["level"]}**。
2. 当前更适合的操作方式是：**{score_info["action"]}**。
3. 核心原因：价格、均线、动能、成交量和消息面综合后，当前处于对应评分区间。

### 二、买卖点地图

- **观察低吸区间**：{format_price(trade_map["watch_low"])} - {format_price(trade_map["watch_high"])}
- **突破确认点**：{format_price(trade_map["breakout"])}
- **风险止损线**：{format_price(trade_map["stop_loss"])}

### 三、小白怎么理解

- 如果价格回到观察区间附近，并且没有继续放量下跌，可以继续观察低吸机会。
- 如果价格放量突破确认点，说明短线资金可能重新增强。
- 如果价格跌破止损线，说明短线结构走弱，应优先控制风险。
"""


def build_ai_prompt(ticker, stock_name, risk, df, score_info, trade_map, news_items):
    news_text = "\n".join(
        [f"- {item['title']}" for item in news_items[:5]]
    ) if news_items else "暂无高相关个股新闻。"

    recent_data = df.tail(12)[[
        "open", "high", "low", "close", "volume",
        "ma5", "ma10", "ma20", "macd_dif", "macd_dea", "kdj_j"
    ]].to_string()

    display_name = f"{stock_name}（{ticker}）" if stock_name else ticker

    prompt = f"""
你是一个A股/美股短线投资分析助手，请用中文分析，不要输出英文，不要输出HTML，不要输出代码。

股票：{display_name}
风险偏好：{risk}

最近行情数据：
{recent_data}

当前AI量化评分：
- 总分：{score_info["total"]}/100
- 分区：{score_info["level"]}
- 适合操作：{score_info["action"]}
- 趋势结构：{score_info["trend_score"]}/30
- 动能指标：{score_info["momentum_score"]}/20
- 成交量资金：{score_info["volume_score"]}/20
- 风险状态：{score_info["risk_score"]}/15
- 消息面：{score_info["news_score"]}/15

关键技术数据：
- 最新价：{format_price(score_info["latest_close"])}
- MA5：{format_price(score_info["ma5"])}
- MA10：{format_price(score_info["ma10"])}
- MA20：{format_price(score_info["ma20"])}
- MACD DIF：{format_price(score_info["macd_dif"])}
- MACD DEA：{format_price(score_info["macd_dea"])}
- KDJ-J：{format_price(score_info["kdj_j"])}
- 最新成交量：{format_big_number(score_info["volume"])}

买卖点地图：
- 观察低吸区间：{format_price(trade_map["watch_low"])} - {format_price(trade_map["watch_high"])}
- 突破确认点：{format_price(trade_map["breakout"])}
- 风险止损线：{format_price(trade_map["stop_loss"])}

相关新闻：
{news_text}

请按以下结构输出，语言要让小白能看懂，每段都要短，不要空话：

### 一、先给小白看的结论
用3条以内说明现在能不能追、适合观察还是适合小仓试探。

### 二、为什么这么判断
分别从趋势、成交量、MACD/KDJ、消息面解释，每点一句话。

### 三、买卖点地图
明确说明：
1. 观察低吸条件
2. 突破确认条件
3. 止损或离场条件

### 四、核心机会
列出2-3条。

### 五、核心风险
列出2-3条。

### 六、三条规则
给出小白可执行的三条观察规则。
"""

    return prompt


def call_ai_analysis(ticker, stock_name, risk, df, score_info, trade_map, news_items):
    if not is_valid_key():
        return fallback_analysis(ticker, stock_name, score_info, trade_map)

    prompt = build_ai_prompt(ticker, stock_name, risk, df, score_info, trade_map, news_items)

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业但表达通俗的股票分析助手。你的输出必须是中文Markdown，不要HTML，不要代码。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return fallback_analysis(ticker, stock_name, score_info, trade_map) + f"\n\n> AI接口暂时失败，已使用本地稳定分析结果。错误信息：{str(e)}"


# =====================================================
# 页面头部
# =====================================================
st.markdown(
    """
<div class="hero">
    <div class="hero-title">📊 AI股票分析平台</div>
    <div class="hero-sub">输入股票代码，快速生成K线趋势、AI评分、买卖点地图和小白可读解读。</div>
    <span class="tag">A股逻辑</span>
    <span class="tag">真实K线</span>
    <span class="tag">AI评分</span>
    <span class="tag">手机端H5</span>
</div>
""",
    unsafe_allow_html=True
)


# =====================================================
# 参数输入卡片
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ 参数设置</div>', unsafe_allow_html=True)

raw_ticker = st.text_input(
    "股票代码",
    value="000066",
    placeholder="例如：000066、000066.SZ、601881、AAPL"
)

stock_name = st.text_input(
    "股票名称",
    value="中国长城",
    placeholder="例如：中国长城、中国银河、英伟达"
)

period = st.selectbox(
    "分析周期",
    ["5d", "1mo", "3mo", "6mo", "1y"],
    index=1
)

risk = st.selectbox(
    "风险偏好",
    ["低", "中", "高"],
    index=1
)

start_btn = st.button("🚀 开始分析")

st.markdown(
    """
<div style="margin-top:12px;color:#6b7280;font-size:12px;font-weight:650;line-height:1.7;">
A股支持：000066、000066.SZ、601881、601881.SS。<br/>
美股支持：AAPL、NVDA、TSLA。
</div>
""",
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 默认说明
# =====================================================
if not start_btn:
    st.markdown(
        """
<div class="card">
    <div class="section-title">📱 使用说明</div>
    <div class="tip">
    这是手机端适配版：输入股票代码后，会按移动端阅读顺序展示 K线图、AI评分、买卖点地图、技术指标、消息面和AI解读。
    </div>
</div>
""",
        unsafe_allow_html=True
    )
    st.stop()


# =====================================================
# 分析流程
# =====================================================
ticker = normalize_ticker(raw_ticker)

with st.spinner("正在获取行情数据与生成AI分析..."):
    data = fetch_price_data(ticker, period)

if data.empty:
    st.error("❌ 没有获取到行情数据。A股请尝试：000066.SZ、601881.SS；美股请尝试：AAPL。")
    st.stop()

df = add_indicators(data)

if df.empty or "close" not in df.columns:
    st.error("❌ 数据缺少收盘价，无法继续分析。")
    st.stop()

news_items = fetch_news(ticker, stock_name)
score_info = calculate_score(df, risk, news_items)
trade_map = calculate_trade_map(df, score_info)


# =====================================================
# K线区域
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">📈 {html_lib.escape(ticker)} K线趋势</div>',
    unsafe_allow_html=True
)

fig = build_kline_chart(df, ticker)
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# AI评分
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧠 AI综合评分</div>', unsafe_allow_html=True)
render_score(score_info)
st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 买卖点地图
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎯 买卖点地图</div>', unsafe_allow_html=True)

decision_card(
    "🟢 观察买点",
    f'{format_price(trade_map["watch_low"])} - {format_price(trade_map["watch_high"])}',
    "价格回到短期均线附近，并且没有继续放量下跌时，再观察低吸机会。"
)

decision_card(
    "🚀 突破确认点",
    format_price(trade_map["breakout"]),
    "放量突破近期高点，说明短线资金可能重新增强；没有放量则谨慎。"
)

decision_card(
    "🔴 风险止损线",
    format_price(trade_map["stop_loss"]),
    "跌破该位置说明短线结构转弱，优先控制风险，不硬扛。"
)

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 技术指标摘要
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📌 技术指标摘要</div>', unsafe_allow_html=True)

st.markdown(
    f"""
<div class="metric-grid">
    {metric_card("MA5", format_price(score_info["ma5"]), "5日均线")}
    {metric_card("MA10", format_price(score_info["ma10"]), "10日均线")}
    {metric_card("MA20", format_price(score_info["ma20"]), "20日均线")}
    {metric_card("MACD DIF", format_price(score_info["macd_dif"]), "短线动能")}
    {metric_card("KDJ-J", format_price(score_info["kdj_j"]), "情绪热度")}
    {metric_card("成交量", format_big_number(score_info["volume"]), "最新成交量")}
</div>
""",
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 新闻
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_news(news_items)
st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# AI解读
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🤖 AI小白解读</div>', unsafe_allow_html=True)

analysis_text = call_ai_analysis(
    ticker=ticker,
    stock_name=stock_name,
    risk=risk,
    df=df,
    score_info=score_info,
    trade_map=trade_map,
    news_items=news_items
)

st.markdown('<div class="ai-box">', unsafe_allow_html=True)
st.markdown(analysis_text)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 原始数据
# =====================================================
with st.expander("查看原始行情数据"):
    st.dataframe(df.tail(30), use_container_width=True)

st.markdown('<div class="bottom-safe"></div>', unsafe_allow_html=True)
