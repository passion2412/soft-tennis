import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Doubles Stats", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のDF']
items_lost = ['DF', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手エース', '相手Sエース']

if 'history' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "パートナー"
    })

# --- 2. カウント関数 ---
def add_point(item, is_win):
    p_num = st.session_state.active_player
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[item] += 1
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 3. CSS (iPhone専用・絶対死守設定) ---
st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコア表示をコンパクトに */
    .score-ui {
        background: #333; color: white; border-radius: 8px;
        text-align: center; padding: 5px; margin-bottom: 10px;
    }

    /* 横並びを絶対に維持(1:1分割) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; gap: 4px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0 !important; }

    /* ボタンの文字を絶対に見せる */
    div.stButton > button {
        width: 100% !important; height: 45px !important;
        font-size: 11px !important; /* 画面に収めるため小さく */
        font-weight: bold !important;
        border-radius: 6px !important;
        color: white !important;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5); /* 文字の輪郭を強調 */
        padding: 0px !important;
    }
    
    /* 得点(青) / 失点(赤) */
    [data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #0056b3 !important; }
    [data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #d32f2f !important; }

    /* ボタン内のテキスト消滅防止 */
    div.stButton > button p { color: white !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. UI描画 ---
# スコア
st.markdown(f"""
<div class="score-ui">
    <div style="font-size: 16px;">{st.session_state.p1_name} & {st.session_state.p2_name} ペア</div>
    <div style="font-size: 32px; font-weight: bold; color: #4CAF50;">
        {st.session_state.p1_games} <span style="font-size:14px; color:white;">games</span> {st.session_state.p2_games}
    </div>
    <div style="font-size: 24px; font-weight: bold;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
</div>
""", unsafe_allow_html=True)

# 選手切り替え
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", key="p1"):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", key="p2"):
    st.session_state.active_player = 2
    st.rerun()

# 入力中表示
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold;'>【 {active_name} 】のプレーを入力</div>", unsafe_allow_html=True)

# ヘッダー
h1, h2 = st.columns(2)
h1.markdown("<div style='text-align:center; color:#0056b3; font-size:11px; font-weight:bold;'>▼ 得点</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; color:#d32f2f; font-size:11px; font-weight:bold;'>▼ 失点</div>", unsafe_allow_html=True)

# --- 5. 入力ボタン (ここが死守ポイント) ---
for w, l in zip(items_won, items_lost):
    col_w, col_l = st.columns(2)
    with col_w:
        st.button(w, key=f"w_{w}", on_click=add_point, args=(w, True))
    with col_l:
        st.button(l, key=f"l_{l}", on_click=add_point, args=(l, False))

# --- 6. 設定・統計 ---
with st.expander("⚙️ 名前設定 / 📊 統計"):
    st.session_state.p1_name = st.text_input("選手1 名前", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2 名前", st.session_state.p2_name)
    st.divider()
    st.write(f"**{st.session_state.p1_name}**の統計", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**の統計", pd.Series(st.session_state.p2_stats))
    if st.button("リセット"):
        st.session_state.clear()
        st.rerun()

