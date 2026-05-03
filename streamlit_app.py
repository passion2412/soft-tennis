import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "選手1", 'p2_name': "選手2"
    })

# --- 2. カウント関数 ---
def add_point(item, is_win):
    p_num = st.session_state.active_player
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[item] += 1
    
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # ゲーム終了判定 (4ポイント先取、2点差)
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 3. CSS（2列固定・白背景・黒文字） ---
st.markdown("""
<style>
    /* 全体の背景と文字色 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード */
    .score-card {
        text-align: center; border: 2px solid #333; padding: 15px; 
        border-radius: 12px; background-color: #f8f9fa; margin-bottom: 20px;
    }

    /* iPhone縦画面でも絶対に2列を維持する設定 */
    [data-testid="column"] {
        flex: 1 1 calc(50% - 10px) !important;
        min-width: calc(50% - 10px) !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
    }

    /* ボタンの色と形 */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 10px !important;
    }
    /* 青ボタン(得点) */
    div.win-btn button { background-color: #007AFF !important; }
    /* 赤ボタン(失点) */
    div.loss-btn button { background-color: #FF3B30 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
# スコア
st.markdown(f"""
<div class="score-card">
    <div style="font-size: 26px; font-weight: bold; color: black;">
        {st.session_state.p1_games} — {st.session_state.p2_games}
    </div>
    <div style="font-size: 52px; font-weight: 900; color: #007AFF;">
        {st.session_state.p1_score} — {st.session_state.p2_score}
    </div>
    <div style="font-size: 14px; color: #555;">{st.session_state.p1_name} vs {st.session_state.p2_name}</div>
</div>
""", unsafe_allow_html=True)

# 選手切り替え
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

st.divider()

# --- 5. 入力ボタン（ここが核心） ---
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; color:black;'>入力中: {active_name}</p>", unsafe_allow_html=True)

# ヘッダー
h1, h2 = st.columns(2)
h1.markdown("<div style='text-align:center; background:#007AFF; color:white; border-radius:5px; font-weight:bold; padding:3px;'>🔵 得点</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; background:#FF3B30; color:white; border-radius:5px; font-weight:bold; padding:3px;'>🔴 失点</div>", unsafe_allow_html=True)

# ボタンリストを確実に2列で配置
for w_item, l_item in zip(items_won, items_lost):
    col_w, col_l = st.columns(2)
    with col_w:
        st.markdown('<div class="win-btn">', unsafe_allow_html=True)
        st.button(w_item, key=f"btn_{w_item}", on_click=add_point, args=(w_item, True))
        st.markdown('</div>', unsafe_allow_html=True)
    with col_l:
        st.markdown('<div class="loss-btn">', unsafe_allow_html=True)
        st.button(l_item, key=f"btn_{l_item}", on_click=add_point, args=(l_item, False))

# --- 6. 統計とリセット ---
st.divider()
if st.checkbox("📊 統計表示"):
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()
