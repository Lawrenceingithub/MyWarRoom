import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 系統設定與初始化 
# ==========================================
st.set_page_config(page_title="戰術雷達 V1.6", layout="wide", page_icon="🎯")

if 'my_portfolio' not in st.session_state:
    st.session_state.my_portfolio = [
        {"代碼": "NVDA", "成本": 190.88, "股數": 20, "均線": 20, "容忍度": 1.5},
        {"代碼": "CEG", "成本": 259.59, "股數": 10, "均線": 20, "容忍度": 1.5},
        {"代碼": "ETN", "成本": 412.97, "股數": 18, "均線": 20, "容忍度": 1.5},
        {"代碼": "3690.HK", "成本": 77.0, "股數": 200, "均線": 60, "容忍度": 2.5},
        {"代碼": "0939.HK", "成本": 7.7, "股數": 2000, "均線": 60, "容忍度": 2.0},
        {"代碼": "1919.HK", "成本": 15.49, "股數": 500, "均線": 60, "容忍度": 3.0}
    ]

st.title("🦅 戰術雷達監控中心 V1.6 (完整偵察版)")

# ==========================================
# 2. 側邊欄：動態配置面板
# ==========================================
with st.sidebar:
    st.header("⚙️ 陣地配置")
    edited_df = st.data_editor(
        pd.DataFrame(st.session_state.my_portfolio),
        num_rows="dynamic",
        key="portfolio_editor"
    )
    if st.button("💾 儲存並同步", use_container_width=True):
        st.session_state.my_portfolio = edited_df.to_dict('records')
        st.success("部隊配置已更新！")

# ==========================================
# 3. 核心運算邏輯
# ==========================================
@st.cache_data(ttl=60)
def analyze_stock(ticker, ma_window, max_volatility):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if len(hist) < ma_window + 1: return None
        hist[f'MA_{ma_window}'] = hist['Close'].rolling(window=ma_window).mean()
        latest, prev = hist.iloc[-1], hist.iloc[-2]
        price, ma_val = latest['Close'], latest[f'MA_{ma_window}']
        change = ((price - prev['Close']) / prev['Close']) * 100
        dist = ((price - ma_val) / ma_val) * 100
        can_buy = (-1.0 <= dist <= 2.0) and (abs(change) <= max_volatility)
        return {"price": price, "change": change, "ma": ma_val, "dist": dist, "can_buy": can_buy}
    except: return None

# ==========================================
# 4. 主介面渲染
# ==========================================
st.markdown("---")
tab1, tab2 = st.tabs(["🛡️ 核心陣地監控", "🔍 單兵偵察系統"])

# ---------- 第一頁：核心持倉 ----------
with tab1:
    portfolio = st.session_state.my_portfolio
    cols = st.columns(3)
    for i, stock in enumerate(portfolio):
        with cols[i % 3]:
            ticker = stock['代碼']
            res = analyze_stock(ticker, stock['均線'], stock['容忍度'])
            st.markdown(f"### 🎯 {ticker}")
            if res:
                st.metric("目前市價", f"${res['price']:.2f}", f"{res['change']:.2f}%")
                st.metric(f"MA{stock['均線']} 防線", f"${res['ma']:.2f}", f"距離 {res['dist']:.2f}%", delta_color="inverse")
                if res['can_buy']: st.success("🟢 穩定進入伏擊區")
                elif res['dist'] < -1.0: st.error("🚨 跌破防線")
                elif abs(res['change']) > stock['容忍度']: st.warning("🟡 波動過大，暫緩")
                else: st.info("⚪ 觀望中")
            st.markdown("<br>", unsafe_allow_html=True)

# ---------- 第二頁：自由查詢 ----------
with tab2:
    st.markdown("### 📡 輸入目標座標，系統將自動計算最佳開火點")
    
    input_col1, input_col2, input_col3 = st.columns(3)
    with input_col1:
        search_ticker = st.text_input("股票代碼 (例: AAPL, FCX, 0939.HK)", value="FCX").upper()
    with input_col2:
        search_ma = st.selectbox("設定防禦均線 (MA)", options=[10, 20, 50, 60, 100, 200], index=3)
    with input_col3:
        search_vol = st.slider("單日容忍波幅 (%)", min_value=0.5, max_value=10.0, value=3.5, step=0.5)

    if st.button("🚀 啟動深度掃描", use_container_width=True):
        with st.spinner('雷達掃描中...'):
            search_data = analyze_stock(search_ticker, search_ma, search_vol)
            if search_data:
                st.markdown(f"### 掃描報告: {search_ticker}")
                st.markdown("---")
                s_col1, s_col2 = st.columns(2)
                s_col1.metric("目前市價", f"${search_data['price']:.2f}", f"今日波動 {search_data['change']:.2f}%")
                s_col2.metric(f"🎯 買入防線 (MA{search_ma})", f"${search_data['ma']:.2f}", f"距離 {search_data['dist']:.2f}%", delta_color="inverse")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if search_data['can_buy']: 
                    st.success("⚡ 戰術判定: 🟢 允許開火 (股價穩定，完美契合安全伏擊條件)")
                elif search_data['dist'] < -1.0: 
                    st.error("⚡ 戰術判定: 🚨 跌破防線 (支撐可能失效，嚴格停止買入)")
                elif abs(search_data['change']) > search_vol:
                    st.warning(f"⚡ 戰術判定: 🟡 暫緩開火 (單日波動 {search_data['change']:.2f}% 超出安全極限 {search_vol}%)")
                else: 
                    st.info("⚡ 戰術判定: 🔴 停止行動 (價格遠離防線，耐心等待回撤)")
            else:
                st.error("⚠️ 無法獲取該座標數據，請確認股票代碼是否正確。")