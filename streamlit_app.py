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
        'active_player': 1, 'p1_name': "選手1", 'p2_name': "選手2"
    })

# --- 2. カウント関数 (Python側で確実に実行) ---
def add_point(item, is_win):
    p_num = st.session_state.active_player
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[item] += 1
    
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # 4ポイント先取、2点差判定
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 3. CSS (iPhone 2列固定 & 高コントラスト) ---
st.markdown("""
<style>
    /* 1. 背景を白に固定 */
    .stApp { background-color: white !important; }
    
    /* 2. スコアボード */
    .score-ui {
        background: #f0f2f6; border: 2px solid black; border-radius: 12px;
        text-align: center; padding: 10px; margin-bottom: 20px; color: black;
    }

    /* 3. ボタンの横並びを絶対維持 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* 改行禁止 */
        gap: 8px !important;
    }
    [data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 45% !important;
    }

    /* 4. ボタンのデザイン上書き */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: none !important;
        color: white !important; /* 文字は白 */
    }

    /* 得点(左列)ボタン: 青 */
    [data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #007AFF !important;
    }
    /* 失点(右列)ボタン: 赤 */
    [data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #FF3B30 !important;
    }
    
    /* ボタンの中のテキストが消えないように保護 */
    div.stButton > button p {
        color: white !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
# スコア表示
st.markdown(f"""
<div class="score-ui">
    <div style="font-size: 24px; font-weight: bold;">{st.session_state.p1_games} — {st.session_state.p2_games}</div>
    <div style="font-size: 48px; font-weight: 900; color: #007AFF;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 14px; color: #333;">{st.session_state.p1_name} vs {st.session_state.p2_name}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", key="sel1"):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", key="sel2"):
    st.session_state.active_player = 2
    st.rerun()

st.divider()

# --- 5. 入力パネル (ここが核心) ---
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; color:black; margin-bottom:10px;'>入力中: {active_name}</p>", unsafe_allow_html=True)

# ヘッダー (横並び)
h1, h2 = st.columns(2)
h1.markdown("<div style='text-align:center; background:#007AFF; color:white; border-radius:5px; font-size:12px; font-weight:bold;'>得点</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; background:#FF3B30; color:white; border-radius:5px; font-size:12px; font-weight:bold;'>失点</div>", unsafe_allow_html=True)

# ボタンリストを1行ずつ確実に2列で表示
for w_item, l_item in zip(items_won, items_lost):
    row_c1, row_c2 = st.columns(2)
    with row_c1:
        st.button(w_item, key=f"win_{w_item}", on_click=add_point, args=(w_item, True))
    with row_c2:
        st.button(l_item, key=f"loss_{l_item}", on_click=add_point, args=(l_item, False))

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計を表示"):
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()

