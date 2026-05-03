import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 (項目を完全に復元) ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア", 'match_name': "今日の試合"
    })

# --- 2. カウント処理 (乱数URLで確実動作) ---
q = st.query_params
if "act" in q:
    item = q["item"]
    is_win = q["win"] == "t"
    stats = st.session_state.p1_stats if st.session_state.active_player == 1 else st.session_state.p2_stats
    if item in stats:
        stats[item] += 1
        if is_win: st.session_state.p1_score += 1
        else: st.session_state.p2_score += 1
        # 4ポイント先取判定
        p1, p2 = st.session_state.p1_score, st.session_state.p2_score
        if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
            if p1 > p2: st.session_state.p1_games += 1
            else: st.session_state.p2_games += 1
            st.session_state.p1_score, st.session_state.p2_score = 0, 0
    st.query_params.clear()
    st.rerun()

# --- 3. CSS (1pxも妥協しない画面固定) ---
st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード */
    .match-title { text-align: center; font-size: 14px; font-weight: bold; color: #555; margin-bottom: 2px; }
    .score-board {
        width: 100%; background: #222; color: white; border-radius: 8px;
        text-align: center; padding: 8px 0; margin-bottom: 8px;
    }

    /* ボタンコンテナ (絶対2列) */
    .btn-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 4px; width: 100%; margin: 0 auto;
    }

    /* ボタン（リンク）を物理固定 */
    .btn {
        display: flex; align-items: center; justify-content: center;
        height: 44px; border-radius: 5px; text-decoration: none !important;
        font-size: 11.5px !important; font-weight: 800 !important;
        color: white !important; text-align: center; line-height: 1.1;
        padding: 0 2px;
    }
    .w-btn { background-color: #007AFF !important; }
    .l-btn { background-color: #FF3B30 !important; }

    /* 選手名ボタン */
    .stButton > button { font-size: 12px !important; height: 35px !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. UI描画 ---
st.markdown(f'<div class="match-title">{st.session_state.match_name}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="score-board">
    <div style="font-size: 12px; opacity: 0.8;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
    <div style="font-size: 36px; font-weight: 900; line-height: 1;">
        {st.session_state.p1_score} <span style="font-size:18px;">-</span> {st.session_state.p2_score}
    </div>
    <div style="font-size: 14px; color: #4CAF50; margin-top: 4px;">Game: {st.session_state.p1_games} - {st.session_state.p2_games}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", key="p1", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", key="p2", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# 入力中ラベル
cur_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; margin: 4px 0;'>記録中: {cur_name}</div>", unsafe_allow_html=True)

# --- 5. 入力パネル (項目名完全復元) ---
html = '<div class="btn-grid">'
for w, l in zip(items_won, items_lost):
    r = random.randint(0, 999)
    html += f'<a href="?act=c&item={w}&win=t&r={r}" target="_self" class="btn w-btn">{w}</a>'
    html += f'<a href="?act=c&item={l}&win=f&r={r}" target="_self" class="btn l-btn">{l}</a>'
html += '</div>'
st.markdown(html, unsafe_allow_html=True)

# --- 6. 設定・統計 (画面下部に配置) ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("⚙️ 名前・試合名の設定 / 📊 統計"):
    st.session_state.match_name = st.text_input("試合名", st.session_state.match_name)
    st.session_state.p1_name = st.text_input("選手1 (自分)", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2 (ペア)", st.session_state.p2_name)
    
    st.divider()
    col_a, col_b = st.columns(2)
    col_a.write(f"**{st.session_state.p1_name}**")
    col_a.table(pd.Series(st.session_state.p1_stats, name="回数"))
    col_b.write(f"**{st.session_state.p2_name}**")
    col_b.table(pd.Series(st.session_state.p2_stats, name="回数"))
    
    if st.button("データをリセットする", use_container_width=True):
        st.session_state.clear()
        st.rerun()
