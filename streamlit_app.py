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
    # スコア判定
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 3. CSS (文字色と横幅を強制固定) ---
st.markdown("""
<style>
    /* 1. 背景を白、ベース文字色を黒に固定 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* 2. ボタンの文字色と背景色を強制指定 */
    /* 全ボタン共通 */
    div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        margin-bottom: -10px !important;
    }
    
    /* 左側(得点)ボタン: 青背景に白文字 */
    [data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
    }
    
    /* 右側(失点)ボタン: 赤背景に白文字 */
    [data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #FF3B30 !important;
        color: white !important;
    }

    /* 3. スマッシュ等の文字が見えないのを防ぐため、ボタン内のテキスト色を再定義 */
    div.stButton > button p {
        color: white !important;
    }

    /* 4. 2列横並びをiPhoneでも強制 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="column"] {
        width: 49% !important;
        flex: 1 1 auto !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
st.markdown(f"""
<div style="text-align: center; border: 2px solid black; padding: 10px; border-radius: 10px; background-color: #f0f2f6;">
    <div style="font-size: 24px; font-weight: bold; color: black;">{st.session_state.p1_games} — {st.session_state.p2_games}</div>
    <div style="font-size: 48px; font-weight: bold; color: #007AFF;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 14px; color: black;">{st.session_state.p1_name} vs {st.session_state.p2_name}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
if c1.button(st.session_state.p1_name, key="sel1", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(st.session_state.p2_name, key="sel2", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

st.divider()

# --- 5. 入力エリア (ここが死守ポイント) ---
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; color:black;'>入力中: {active_name}</p>", unsafe_allow_html=True)

# 1行ずつ確実に2列で表示
for w_item, l_item in zip(items_won, items_lost):
    row_c1, row_c2 = st.columns(2)
    with row_c1:
        st.button(w_item, key=f"w_{w_item}", on_click=add_point, args=(w_item, True))
    with row_c2:
        st.button(l_item, key=f"l_{l_item}", on_click=add_point, args=(l_item, False))

# --- 6. 統計 ---
if st.checkbox("📊 統計表示"):
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
