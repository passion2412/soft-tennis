import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['エース', 'リターン', 'スマッシュ', 'ボレー', 'ミス', 'DF']
items_lost = ['DF', 'リターンミス', 'スマッシュミス', 'ミス', 'ボレーミス', '相手エース']

if 'history' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア"
    })

# --- 2. カウント処理 (URLクエリを確実にキャッチ) ---
q = st.query_params
if "act" in q:
    item = q["item"]
    is_win = q["win"] == "t"
    stats = st.session_state.p1_stats if st.session_state.active_player == 1 else st.session_state.p2_stats
    stats[item] = stats.get(item, 0) + 1
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # 4ポイント先取判定
    if (st.session_state.p1_score >= 4 or st.session_state.p2_score >= 4) and abs(st.session_state.p1_score - st.session_state.p2_score) >= 2:
        if st.session_state.p1_score > st.session_state.p2_score: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0
    st.query_params.clear()
    st.rerun()

# --- 3. CSS (iPhoneの全機能を封じ込める) ---
st.markdown("""
<style>
    /* 1. 背景と文字色を白黒に完全固定 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* 2. スコアボードを極限まで薄く */
    .score-board {
        width: 100%; background: #333; color: white; border-radius: 10px;
        text-align: center; padding: 10px 0; margin-bottom: 10px;
    }

    /* 3. ボタンエリアをiPhoneの画面幅(320px〜)に完全対応させる */
    .btn-container {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 4px; width: 100%; max-width: 400px; margin: 0 auto;
    }

    /* 4. ボタンを「リンク」として再定義。これで文字が消えるのを防ぐ */
    .count-btn {
        display: flex; align-items: center; justify-content: center;
        height: 48px; border-radius: 6px; text-decoration: none !important;
        font-size: 13px !important; font-weight: 900 !important;
        color: white !important; /* 文字色は絶対白 */
        box-shadow: none !important; outline: none !important;
    }
    .win-btn { background-color: #007AFF !important; }
    .loss-btn { background-color: #FF3B30 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
st.markdown(f"""
<div class="score-board">
    <div style="font-size: 14px;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
    <div style="font-size: 40px; font-weight: bold; line-height: 1.2;">
        {st.session_state.p1_score} <span style="font-size:20px;">-</span> {st.session_state.p2_score}
    </div>
    <div style="font-size: 16px; color: #4CAF50;">Game: {st.session_state.p1_games} - {st.session_state.p2_games}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択（ここだけ標準ボタンで安定）
c1, c2 = st.columns(2)
if c1.button(st.session_state.p1_name, key="p1", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(st.session_state.p2_name, key="p2", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 入力ボタン (HTMLリンク方式で死守) ---
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-weight:bold; margin: 10px 0;'>入力中: {active_name}</div>", unsafe_allow_html=True)

import random
btn_html = '<div class="btn-container">'
for w, l in zip(items_won, items_lost):
    r = random.randint(0,999)
    # 青ボタン(得点)
    btn_html += f'<a href="?act=c&item={w}&win=t&r={r}" target="_self" class="count-btn win-btn">{w}</a>'
    # 赤ボタン(失点)
    btn_html += f'<a href="?act=c&item={l}&win=f&r={r}" target="_self" class="count-btn loss-btn">{l}</a>'
btn_html += '</div>'

st.markdown(btn_html, unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計表示"):
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))
    if st.button("リセット"):
        st.session_state.clear()
        st.rerun()
