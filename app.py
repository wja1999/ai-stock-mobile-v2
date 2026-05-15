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

st.set_page_config(
    page_title="AI股票分析平台",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
html, body, .stApp {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

* {
    box-sizing: border-box !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    width: 100% !important;
    max-width: 430px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    overflow-x: hidden !important;
}

.block-container {
    padding: 16px 14px 96px !important;
}

.element-container,
.stMarkdown,
[data-testid="stMarkdownContainer"],
[data-testid="stVerticalBlock"],
[data-testid="column"] {
    max-width: 100% !important;
    overflow-x: visible !important;
    overflow-y: visible !important;
}

[data-testid="column"] > div,
[data-testid="stVerticalBlock"] > div,
.element-container > div {
    overflow: visible !important;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(239,68,68,.16), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(251,191,36,.16), transparent 34%),
        linear-gradient(180deg, #fff7f2 0%, #f8f8fb 42%, #fff 100%);
}

#MainMenu, footer, header, .stDeployButton {
    visibility: hidden !important;
    display: none !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

h1,h2,h3,h4,h5,h6,p,li,span,div {
    color: #111827;
}

.stButton button,
.stFormSubmitButton button {
    width: 100%;
    height: 50px;
    border-radius: 999px;
    border: none;
    background: linear-gradient(90deg,#ef4444,#ff6a18);
    color: #fff !important;
    font-weight: 950;
    font-size: 16px;
    box-shadow: 0 14px 28px rgba(239,68,68,.26);
}

.landing-hero {
    background:
        radial-gradient(circle at 80% 20%, rgba(255,216,102,.38), transparent 32%),
        linear-gradient(135deg, #fff4eb 0%, #ffffff 58%, #fff0f0 100%);
    border: 1px solid rgba(239,68,68,.14);
    border-radius: 28px;
    padding: 24px 18px 20px;
    box-shadow: 0 18px 42px rgba(239,68,68,.12);
    margin-bottom: 14px;
}

.landing-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(239,68,68,.10);
    color: #dc2626;
    font-size: 12px;
    font-weight: 900;
}

.landing-title {
    font-size: 30px;
    font-weight: 950;
    line-height: 1.15;
    margin-top: 14px;
    letter-spacing: -0.5px;
}

.landing-sub {
    margin-top: 10px;
    color: #5b6472;
    font-size: 14px;
    line-height: 1.65;
    font-weight: 700;
}

.price-card {
    margin-top: 18px;
    background: linear-gradient(135deg, #ef4444, #ff6a18);
    border-radius: 22px;
    padding: 18px;
    color: #fff;
    box-shadow: 0 18px 36px rgba(239,68,68,.26);
}

.price-label {
    color: rgba(255,255,255,.86);
    font-size: 13px;
    font-weight: 850;
}

.price-main {
    margin-top: 6px;
    color: #fff;
    font-size: 46px;
    font-weight: 950;
    line-height: 1;
}

.price-main span {
    color: #fff;
    font-size: 18px;
    font-weight: 900;
}

.price-desc {
    margin-top: 10px;
    color: rgba(255,255,255,.94);
    font-size: 14px;
    line-height: 1.5;
    font-weight: 800;
}

.landing-card {
    background: rgba(255,255,255,.96);
    border: 1px solid #edf0f5;
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
    margin-top: 13px;
}

.landing-section-title {
    font-size: 19px;
    font-weight: 950;
    margin-bottom: 12px;
}

.benefit-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.benefit-item {
    background: linear-gradient(135deg,#fff7f4,#fff);
    border: 1px solid rgba(239,68,68,.10);
    border-radius: 16px;
    padding: 13px;
    min-height: 96px;
}

.benefit-icon {
    font-size: 24px;
    margin-bottom: 8px;
}

.benefit-title {
    font-size: 15px;
    font-weight: 950;
}

.benefit-desc {
    margin-top: 5px;
    color: #6b7280;
    font-size: 12px;
    line-height: 1.45;
    font-weight: 700;
}

.unlock-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 16px;
    padding: 13px;
    margin-top: 10px;
}

.unlock-icon {
    width: 38px;
    height: 38px;
    border-radius: 13px;
    background: linear-gradient(135deg,#f59e0b,#ef4444);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 950;
    flex-shrink: 0;
}

.unlock-title {
    font-size: 15px;
    font-weight: 950;
}

.unlock-desc {
    margin-top: 3px;
    font-size: 12px;
    color: #7c2d12;
    line-height: 1.45;
    font-weight: 700;
}

.bottom-cta {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 430px;
    padding: 10px 14px 18px;
    background: rgba(255,255,255,.92);
    backdrop-filter: blur(14px);
    border-top: 1px solid rgba(229,231,235,.9);
    z-index: 999;
}

.secondary-btn button {
    background: #fff !important;
    color: #ef4444 !important;
    border: 1px solid rgba(239,68,68,.22) !important;
    box-shadow: none !important;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 2px 2px 14px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg,#ef4444,#2563eb);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 19px;
    font-weight: 900;
    box-shadow: 0 10px 18px rgba(239,68,68,.18);
}

.brand-title {
    font-size: 22px;
    font-weight: 950;
    line-height: 1.1;
}

.brand-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 3px;
    font-weight: 650;
}

.help-btn {
    padding: 8px 10px;
    border: 1px solid #e5e7eb;
    background: #fff;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    color: #4b5563;
    box-shadow: 0 6px 16px rgba(15,23,42,.05);
}

.section-title {
    font-size: 18px;
    font-weight: 950;
    margin: 18px 0 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.stForm {
    width: 100%;
    background: rgba(255,255,255,.96);
    border: 1px solid #edf0f5;
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 10px 28px rgba(15,23,42,.07);
    overflow: visible !important;
}

.stTextInput label,
.stSelectbox label {
    color: #6b7280 !important;
    font-weight: 850 !important;
    font-size: 12px !important;
}

.stTextInput input {
    height: 44px !important;
    border-radius: 13px !important;
    border: 1px solid #e5e7eb !important;
    background: #fff !important;
    color: #111827 !important;
    font-size: 15px !important;
    font-weight: 850 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 13px !important;
    border: 1px solid #e5e7eb !important;
    background: #fff !important;
    color: #111827 !important;
    font-size: 15px !important;
    font-weight: 850 !important;
}

.support-text {
    margin-top: 10px;
    color: #6b7280;
    font-size: 12px;
    font-weight: 700;
    line-height: 1.65;
}

.score-card {
    width: 100%;
    background: linear-gradient(135deg,#fff7f4,#fff);
    border: 1px solid rgba(239,68,68,.14);
    border-radius: 18px;
    padding: 14px;
    overflow: visible !important;
    height: auto !important;
}

.score-label {
    color: #6b7280;
    font-size: 12px;
    font-weight: 850;
    margin-bottom: 8px;
}

.score-num {
    font-size: 42px;
    line-height: 1;
    font-weight: 950;
    color: #ef4444;
}

.score-total {
    font-size: 17px;
    color: #9ca3af;
    font-weight: 850;
}

.score-status {
    font-size: 18px;
    margin-top: 10px;
    font-weight: 950;
}

.score-desc {
    font-size: 12px;
    line-height: 1.55;
    color: #4b5563;
    margin-top: 6px;
    font-weight: 650;
}

.progress-bg {
    height: 9px;
    background: #fee2e2;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 12px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg,#ef4444,#f97316);
    border-radius: 999px;
}

.metric-card {
    background: #fff;
    border: 1px solid #edf0f5;
    border-radius: 16px;
    padding: 13px;
    min-height: 88px;
    height: auto !important;
    overflow: visible !important;
}

.metric-label {
    color: #6b7280;
    font-size: 12px;
    font-weight: 850;
}

.metric-value {
    margin-top: 8px;
    color: #111827;
    font-size: 22px;
    font-weight: 950;
    line-height: 1.1;
    word-break: break-word;
}

.metric-sub {
    color: #9ca3af;
    font-size: 11px;
    font-weight: 700;
    margin-top: 6px;
}

.decision-card {
    border-radius: 16px;
    padding: 14px;
    border: 1px solid #edf0f5;
    margin-bottom: 10px;
    overflow: visible !important;
    height: auto !important;
}

.buy-card {
    background: linear-gradient(135deg,#effdf4,#ffffff);
}

.break-card {
    background: linear-gradient(135deg,#fff7ed,#ffffff);
}

.risk-card {
    background: linear-gradient(135deg,#fff1f2,#ffffff);
}

.decision-title {
    font-size: 15px;
    font-weight: 950;
}

.decision-price {
    margin-top: 8px;
    font-size: 22px;
    font-weight: 950;
    color: #ef4444;
}

.decision-text {
    margin-top: 8px;
    color: #4b5563;
    font-size: 13px;
    line-height: 1.6;
    font-weight: 700;
}

.news-item {
    background: #fff;
    border: 1px solid #edf0f5;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
    overflow: visible !important;
    height: auto !important;
}

.news-item a {
    color: #2563eb !important;
    font-size: 13px;
    line-height: 1.5;
    font-weight: 850;
    text-decoration: none;
}

.news-meta {
    margin-top: 6px;
    color: #9ca3af;
    font-size: 11px;
    font-weight: 700;
}

.ai-box {
    background: #fff;
    border: 1px solid #edf0f5;
    border-radius: 16px;
    padding: 14px;
    overflow: visible !important;
    height: auto !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 14px;
    line-height: 1.78;
    color: #1f2937 !important;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-size: 18px !important;
    color: #111827 !important;
    font-weight: 950 !important;
    margin-top: 16px !important;
}

.tip {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
    border-radius: 14px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.65;
    font-weight: 750;
}
</style>
""", unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "landing"


def go_app():
    st.session_state.page = "app"
    st.rerun()


def go_landing():
    st.session_state.page = "landing"
    st.rerun()


def render_landing_page():
    st.markdown("""
<div class="landing-hero">
    <div class="landing-badge">🔥 开户专属权益 · 限时免费</div>
    <div class="landing-title">AI股票分析平台<br/>开通账户免费用</div>
    <div class="landing-sub">
        输入股票代码，即可生成真实K线趋势、AI综合评分、买卖点地图与小白可读交易计划。
    </div>

    <div class="price-card">
        <div class="price-label">工具权益价值</div>
        <div class="price-main">988<span> 元/年</span></div>
        <div class="price-desc">完成股票开户后，即可解锁全年免费使用权益。</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.button("立即开户免费使用", on_click=go_app, use_container_width=True)

    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    st.button("先体验AI分析", on_click=go_app, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
<div class="landing-card">
    <div class="landing-section-title">你将免费获得什么</div>
    <div class="benefit-grid">
        <div class="benefit-item">
            <div class="benefit-icon">📈</div>
            <div class="benefit-title">真实K线趋势</div>
            <div class="benefit-desc">自动读取行情数据，展示价格与成交量变化。</div>
        </div>
        <div class="benefit-item">
            <div class="benefit-icon">🧠</div>
            <div class="benefit-title">AI综合评分</div>
            <div class="benefit-desc">从趋势、动能、资金、风险、消息面综合判断。</div>
        </div>
        <div class="benefit-item">
            <div class="benefit-icon">🎯</div>
            <div class="benefit-title">买卖点地图</div>
            <div class="benefit-desc">给出观察买点、突破确认点和风险止损线。</div>
        </div>
        <div class="benefit-item">
            <div class="benefit-icon">🤖</div>
            <div class="benefit-title">小白解读</div>
            <div class="benefit-desc">不用看复杂指标，直接理解机会和风险。</div>
        </div>
    </div>
</div>

<div class="landing-card">
    <div class="landing-section-title">开户后使用路径</div>
    <div class="unlock-row">
        <div class="unlock-icon">1</div>
        <div>
            <div class="unlock-title">完成股票开户</div>
            <div class="unlock-desc">开通账户后解锁AI分析工具权益。</div>
        </div>
    </div>
    <div class="unlock-row">
        <div class="unlock-icon">2</div>
        <div>
            <div class="unlock-title">输入股票代码</div>
            <div class="unlock-desc">支持A股与部分美股代码查询。</div>
        </div>
    </div>
    <div class="unlock-row">
        <div class="unlock-icon">3</div>
        <div>
            <div class="unlock-title">查看AI交易计划</div>
            <div class="unlock-desc">快速获得评分、趋势和买卖点参考。</div>
        </div>
    </div>
</div>

<div class="landing-card">
    <div class="landing-section-title">为什么值得开户体验</div>
    <div class="tip">
        传统看盘需要理解K线、均线、成交量、MACD、KDJ、消息面等多个维度。这个工具会把复杂信息整理成小白能看懂的交易观察计划，帮助你更快判断机会和风险。
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="bottom-cta">', unsafe_allow_html=True)
    st.button("开户解锁 988元/年权益", on_click=go_app, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def is_valid_key() -> bool:
    return bool(
        DEEPSEEK_API_KEY
        and DEEPSEEK_API_KEY != "这里填你的DeepSeek key"
        and DEEPSEEK_API_KEY != "EMPTY"
    )


def safe_float(value, default=0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def format_price(value) -> str:
    return f"{safe_float(value):.2f}"


def format_big_number(value) -> str:
    value = safe_float(value)
    if abs(value) >= 100000000:
        return f"{value / 100000000:.2f}亿"
    if abs(value) >= 10000:
        return f"{value / 10000:.2f}万"
    return f"{value:.0f}"


def normalize_ticker(raw: str) -> str:
    code = str(raw).strip().upper().replace(" ", "")
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
            new_cols.append(picked if picked else str(col[0]))
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
    return flatten_columns(data)


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


def fetch_news(ticker: str, stock_name: str, max_items: int = 4):
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
            source_node = item.find("source")
            source = source_node.text if source_node is not None else "新闻源"

            title = re.sub(r"\s+-\s+[^-]+$", "", title).strip()

            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "source": source
                })
    except Exception:
        pass

    return items


def score_news(news_items):
    positive_words = ["增长", "盈利", "利好", "中标", "回购", "增持", "突破", "创新高", "上调", "买入", "净利", "业绩预增", "合作", "获批", "订单"]
    negative_words = ["减持", "亏损", "下滑", "处罚", "风险", "诉讼", "问询", "退市", "立案", "违规", "暴跌", "预亏", "警示", "债务"]

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
        action_desc = "已有仓位可继续观察，新增仓位更适合等回踩。"
    elif total >= 65:
        level = "偏强区"
        action = "小仓试探"
        action_desc = "可关注回踩低吸或突破确认，但需要设置止损。"
    elif total >= 50:
        level = "中性区"
        action = "观察为主"
        action_desc = "多空没有明显胜负，等待放量突破或回踩企稳。"
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


def calculate_trade_map(df: pd.DataFrame):
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

    return {
        "watch_low": min(support_main, close),
        "watch_high": max(support_high, close),
        "breakout": recent_high,
        "stop_loss": min(recent_low, close * 0.95),
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
            opacity=0.5,
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
        rangeslider_visible=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False
    )

    fig.update_layout(
        height=292,
        margin=dict(l=2, r=2, t=2, b=2),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#6b7280", size=10),
        xaxis_rangeslider_visible=False
    )

    return fig


def metric_card(label, value, sub=""):
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">{html_lib.escape(str(label))}</div>
    <div class="metric-value">{html_lib.escape(str(value))}</div>
    <div class="metric-sub">{html_lib.escape(str(sub))}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_score(score_info):
    total = score_info["total"]
    width = max(0, min(100, total))

    st.markdown(
        f"""
<div class="score-card">
    <div class="score-label">AI综合评分</div>
    <div>
        <span class="score-num">{total}</span>
        <span class="score-total">/100</span>
    </div>
    <div class="score-status">{html_lib.escape(score_info["level"])} · {html_lib.escape(score_info["action"])}</div>
    <div class="score-desc">{html_lib.escape(score_info["action_desc"])}</div>
    <div class="progress-bg">
        <div class="progress-fill" style="width:{width}%;"></div>
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    items = [
        ("趋势结构", f'{score_info["trend_score"]}/30', "趋势"),
        ("动能指标", f'{score_info["momentum_score"]}/20', "动能"),
        ("成交量资金", f'{score_info["volume_score"]}/20', "量价"),
        ("风险控制", f'{score_info["risk_score"]}/15', "风控"),
        ("消息面", f'{score_info["news_score"]}/15', "情绪"),
        ("最新价", format_price(score_info["latest_close"]), "收盘价"),
        ("利好", f'↑ {score_info["news_pos"]}', "消息"),
        ("风险", f'↓ {score_info["news_neg"]}', "消息"),
    ]

    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            metric_card(*item)


def render_news(news_items):
    if not news_items:
        st.markdown(
            '<div class="tip">暂未抓取到高相关个股新闻，当前分析主要参考K线、成交量、技术指标与AI解读。</div>',
            unsafe_allow_html=True
        )
        return

    for item in news_items:
        title = html_lib.escape(item.get("title", ""))
        link = item.get("link", "")
        source = html_lib.escape(item.get("source", "新闻源"))

        st.markdown(f"""
<div class="news-item">
    <a href="{link}" target="_blank">{title}</a>
    <div class="news-meta">{source}</div>
</div>
""", unsafe_allow_html=True)


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
    news_text = "\n".join([f"- {item['title']}" for item in news_items[:4]]) if news_items else "暂无高相关个股新闻。"

    recent_data = df.tail(12)[[
        "open", "high", "low", "close", "volume",
        "ma5", "ma10", "ma20", "macd_dif", "macd_dea", "kdj_j"
    ]].to_string()

    display_name = f"{stock_name}（{ticker}）" if stock_name else ticker

    return f"""
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

买卖点地图：
- 观察低吸区间：{format_price(trade_map["watch_low"])} - {format_price(trade_map["watch_high"])}
- 突破确认点：{format_price(trade_map["breakout"])}
- 风险止损线：{format_price(trade_map["stop_loss"])}

相关新闻：
{news_text}

请按以下结构输出，语言让小白能看懂，每段都短，不要空话：

### 一、先给小白看的结论
用3条以内说明现在能不能追、适合观察还是适合小仓试探。

### 二、为什么这么判断
分别从趋势、成交量、MACD/KDJ、消息面解释，每点一句话。

### 三、买卖点地图
明确说明观察低吸、突破确认、止损离场条件。

### 四、核心机会
列出2-3条。

### 五、核心风险
列出2-3条。

### 六、三条规则
给出小白可执行的三条观察规则。
"""


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


def render_app_page():
    st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="logo">📊</div>
        <div>
            <div class="brand-title">AI股票分析平台</div>
            <div class="brand-sub">智能分析 · 快速决策 · 小白可读</div>
        </div>
    </div>
    <div class="help-btn">已解锁</div>
</div>
""", unsafe_allow_html=True)

    st.button("返回权益页", on_click=go_landing, use_container_width=True)

    with st.form("stock_form"):
        st.markdown('<div class="section-title">⚙️ 参数设置</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            raw_ticker = st.text_input("股票代码", value="002519", placeholder="例如：002519")
        with c2:
            stock_name = st.text_input("股票名称", value="银河电子", placeholder="例如：银河电子")

        c3, c4 = st.columns(2)
        with c3:
            period = st.selectbox("分析周期", ["5d", "1mo", "3mo", "6mo", "1y"], index=3)
        with c4:
            risk = st.selectbox("风险偏好", ["低", "中", "高"], index=2)

        start_btn = st.form_submit_button("🚀 开始分析")

        st.markdown("""
<div class="support-text">
A股支持：000066、000066.SZ、601881、601881.SS ｜ 美股支持：AAPL、NVDA、TSLA
</div>
""", unsafe_allow_html=True)

    if not start_btn:
        st.markdown('<div class="section-title">📱 使用说明</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tip">输入股票代码后，将按手机端阅读顺序展示 K线图、AI评分、买卖点地图、技术指标、消息面和AI解读。</div>',
            unsafe_allow_html=True
        )
        st.stop()

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
    trade_map = calculate_trade_map(df)

    st.markdown(f'<div class="section-title">📈 {html_lib.escape(ticker)} K线趋势</div>', unsafe_allow_html=True)
    fig = build_kline_chart(df, ticker)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown('<div class="section-title">🧠 AI综合评分</div>', unsafe_allow_html=True)
    render_score(score_info)

    st.markdown('<div class="section-title">🎯 买卖点地图</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="decision-card buy-card">
    <div class="decision-title">🟢 观察买点</div>
    <div class="decision-price">{format_price(trade_map["watch_low"])} - {format_price(trade_map["watch_high"])}</div>
    <div class="decision-text">价格回到短期均线附近，并且没有继续放量下跌时，再观察低吸机会。</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="decision-card break-card">
    <div class="decision-title">🚀 突破确认点</div>
    <div class="decision-price">{format_price(trade_map["breakout"])}</div>
    <div class="decision-text">放量突破近期高点，说明短线资金可能重新增强；没有放量则谨慎。</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="decision-card risk-card">
    <div class="decision-title">🔴 风险止损线</div>
    <div class="decision-price">{format_price(trade_map["stop_loss"])}</div>
    <div class="decision-text">跌破该位置说明短线结构转弱，优先控制风险，不硬扛。</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">📌 技术指标摘要</div>', unsafe_allow_html=True)

    tech_items = [
        ("MA5", format_price(score_info["ma5"]), "5日均线"),
        ("MA10", format_price(score_info["ma10"]), "10日均线"),
        ("MA20", format_price(score_info["ma20"]), "20日均线"),
        ("MACD DIF", format_price(score_info["macd_dif"]), "短线动能"),
        ("KDJ-J", format_price(score_info["kdj_j"]), "情绪热度"),
        ("成交量", format_big_number(score_info["volume"]), "最新成交量"),
    ]

    cols = st.columns(2)
    for i, item in enumerate(tech_items):
        with cols[i % 2]:
            metric_card(*item)

    st.markdown('<div class="section-title">📰 个股消息面</div>', unsafe_allow_html=True)
    render_news(news_items)

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

    with st.expander("查看原始行情数据"):
        st.dataframe(df.tail(30), use_container_width=True)


if st.session_state.page == "landing":
    render_landing_page()
else:
    render_app_page()
