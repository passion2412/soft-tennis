import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のDF']
items_lost = ['DF', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手エース', '相手Sエース']

if 'p1_score' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "選手1", 'p2_name': "選手2"
    })

# --- 2. カウント処理 (URLクエリ方式の安定化) ---
q = st.query_params
if "action" in q:
    item = q["item"]
    is_win = q["win"] == "true"
    p_num = st.session_state.active_player
    
    # 統計加算
    stats = st.session_state.p1_stats if p_num == 1 else st.session_state.p2_stats
    stats[item] = stats.get(item, 0) + 1
    
    # スコア加算
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # ゲーム終了判定
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0
    
    st.query_params.clear()
    st.rerun()

# --- 3. CSS (絶対に崩さないためのガード) ---
st.markdown("""
<style>
    /* 画面全体 */
    .stApp { background-color: white !important; }
    
    /* スコアボード */
    .score-ui {
        background: #f0f2f6; border: 2px solid #333; border-radius: 12px;
        text-align: center; padding: 10px; margin-bottom: 10px; color: black;
    }
    
    /* ボタンコンテナ (2列固定) */
    .btn-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 6px; width: 100%; box-sizing: border-box;
    }
    
    /* ボタン本体 */
    .base-btn {
        display: flex; align-items: center; justify-content: center;
        height: 50px; border-radius: 8px; text-decoration: none;
        font-weight: bold; font-size: 13px; color: white !important;
        border: none;
    }
    .win-color { background-color: #007AFF; } /* 青 */
    .loss-color { background-color: #FF3B30; } /* 赤 */
    
    /* 入力中ラベル */
    .active-label { text-align: center; font-weight: bold; color: black; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- 4. UI描画 ---
# スコア
st.markdown(f"""
<div class="score-ui">
    <div style="font-size: 20px; font-weight: bold;">{st.session_state.p1_games} — {st.session_state.p2_games}</div>
    <div style="font-size: 40px; font-weight: 900; color: #007AFF;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 14px;">{st.session_state.p1_name} vs {st.session_state.p2_name}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択 (ここだけ標準ボタンで安定)
c1, c2 = st.columns(2)
if c1.button(st.session_state.p1_name, use_container_width=True, key="p1_sel"):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(st.session_state.p2_name, use_container_width=True, key="p2_sel"):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 入力パネル (完全固定HTML方式) ---
active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f'<div class="active-label">入力中: {active_name}</div>', unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="btn-grid" style="margin-bottom: 4px;">
    <div style="background:#007AFF; color:white; text-align:center; border-radius:4px; font-size:12px; padding:2px;">得点</div>
    <div style="background:#FF3B30; color:white; text-align:center; border-radius:4px; font-size:12px; padding:2px;">失点</div>
</div>
""", unsafe_allow_html=True)

# ボタン群
import random
html_btns = '<div class="btn-grid">'
for w, l in zip(items_won, items_lost):
    # 重複URLを避けるための乱数
    rnd = random.randint(0, 9999)
    html_btns += f'<a href="?action=click&item={w}&win=true&r={rnd}" target="_self" class="base-btn win-color">{w}</a>'
    html_btns += f'<a href="?action=click&item={l}&win=false&r={rnd}" target="_self" class="base-btn loss-color">{l}</a>'
html_btns += '</div>'

st.markdown(html_btns, unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計"):
    st.write(f"{st.session_state.p1_name}", pd.Series(st.session_state.p1_stats))
    st.write(f"{st.session_state.p2_name}", pd.Series(st.session_state.p2_stats))

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
