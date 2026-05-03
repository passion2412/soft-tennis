import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. セッション状態の初期化 ---
if 'p1_score' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0,
        'p1_games': 0, 'p2_games': 0,
        'p1_stats': {}, 'p2_stats': {},
        'active_player': 1, 'p1_name': "選手1", 'p2_name': "選手2",
        'history': []
    })

# --- 2. 設定エリア ---
with st.expander("📝 名前・試合設定"):
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)

# --- 3. スコア更新ロジック ---
# HTMLコンポーネントからの通知を受け取る
def process_click(btn_label):
    p_num = st.session_state.active_player
    is_win = btn_label in items_won
    
    # 統計加算
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[btn_label] = stats.get(btn_label, 0) + 1
    
    # スコア加算
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # ゲーム終了判定
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# --- 4. スコアボード表示 (白背景・黒文字) ---
st.markdown(f"""
<div style="text-align: center; border: 2px solid black; padding: 10px; border-radius: 10px; background-color: #f9f9f9; color: black; margin-bottom: 10px;">
    <div style="font-size:24px; font-weight:bold;">{st.session_state.p1_games} — {st.session_state.p2_games}</div>
    <div style="font-size:48px; font-weight:bold; color:#007AFF;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
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

# --- 5. 強制2列HTMLボタン (JavaScript通信) ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name

# ボタンクリックをStreamlitに伝えるためのJS
# ここでボタンを押し、Streamlitをリロードさせてカウントを回します
button_html = f"""
<div style="text-align:center; font-family:sans-serif; font-weight:bold; margin-bottom:10px;">入力中: {active_name}</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family:sans-serif;">
    <div style="background:#007AFF; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:14px;">得点</div>
    <div style="background:#FF3B30; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:14px;">失点</div>
"""

for w, l in zip(items_won, items_lost):
    button_html += f"""
    <button onclick="parent.window.location.href='?click={w}'" style="background:#007AFF; color:white; border:none; padding:15px 2px; border-radius:8px; font-weight:bold; font-size:12px;">{w}</button>
    <button onclick="parent.window.location.href='?click={l}'" style="background:#FF3B30; color:white; border:none; padding:15px 2px; border-radius:8px; font-weight:bold; font-size:12px;">{l}</button>
    """
button_html += "</div>"

# URLからクリック情報を取得
q = st.query_params
if "click" in q:
    process_click(q["click"])
    st.query_params.clear()
    st.rerun()

st.markdown(button_html, unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計表示"):
    c_a, c_b = st.columns(2)
    with c_a:
        st.write(f"**{st.session_state.p1_name}**")
        st.table(pd.Series(st.session_state.p1_stats) if st.session_state.p1_stats else "データなし")
    with c_b:
        st.write(f"**{st.session_state.p2_name}**")
        st.table(pd.Series(st.session_state.p2_stats) if st.session_state.p2_stats else "データなし")

if st.button("全データリセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()
