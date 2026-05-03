import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のDF']
items_lost = ['DF', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手エース', '相手Sエース']

if 'history' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア"
    })

# --- 2. カウント関数 ---
def add_point(item, is_win):
    p_num = st.session_state.active_player
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[item] += 1
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    # スコア判定
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 3. CSS (余白削除・2列絶対固定・文字色保護) ---
st.markdown("""
<style>
    /* 1. 全体背景と文字色 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* 2. スコアボードを極限までコンパクトに */
    .score-ui {
        text-align: center; border: 2px solid black; padding: 5px; 
        border-radius: 10px; background-color: #f0f2f6; margin-bottom: 5px;
    }

    /* 3. 2列の余白をゼロにしてiPhone画面に収める */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important; /* 列間の隙間を最小化 */
    }
    [data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 48% !important;
        padding: 0 !important; /* 内部余白を削除 */
    }

    /* 4. ボタンデザインの再定義 */
    div.stButton > button {
        width: 100% !important;
        height: 42px !important; /* 高さを少し抑えて画面内に収める */
        font-weight: bold !important;
        font-size: 12px !important;
        border-radius: 5px !important;
        border: none !important;
        color: white !important;
    }
    
    /* 左(青)・右(赤)の背景色 */
    [data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #007AFF !important; }
    [data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #FF3B30 !important; }

    /* 文字色を白に強制 */
    div.stButton > button p { color: white !important; margin: 0 !important; }
    
    /* 統計テーブルを見やすく */
    .stTable { background-color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
st.markdown(f"""
<div class="score-ui">
    <div style="font-size: 20px; font-weight: bold; color: black;">{st.session_state.p1_games} — {st.session_state.p2_games}</div>
    <div style="font-size: 38px; font-weight: bold; color: #007AFF; line-height: 1;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 12px; color: black;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
if c1.button(st.session_state.p1_name, key="sel1"):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(st.session_state.p2_name, key="sel2"):
    st.session_state.active_player = 2
    st.rerun()

# 入力中ラベル
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:13px; margin:5px 0;'>入力中: {active_name}</p>", unsafe_allow_html=True)

# --- 5. 入力エリア (2列・隙間なし) ---
for w_item, l_item in zip(items_won, items_lost):
    row_c1, row_c2 = st.columns(2)
    with row_c1:
        st.button(w_item, key=f"w_{w_item}", on_click=add_point, args=(w_item, True))
    with row_c2:
        st.button(l_item, key=f"l_{l_item}", on_click=add_point, args=(l_item, False))

# --- 6. 統計と設定 ---
st.divider()
with st.expander("📊 統計・名前設定"):
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))
    if st.button("全リセット"):
        st.session_state.clear()
        st.rerun()
