import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

for key in ['p1_stats', 'p2_stats', 'game_score', 'point_score', 'history', 'game_results']:
    if key not in st.session_state:
        if 'stats' in key: st.session_state[key] = {item: 0 for item in items_won + items_lost}
        elif 'score' in key: st.session_state[key] = [0, 0]
        else: st.session_state[key] = []

if 'active_player' not in st.session_state: st.session_state.active_player = 1
if 'p1_name' not in st.session_state: st.session_state.p1_name = "選手1"
if 'p2_name' not in st.session_state: st.session_state.p2_name = "選手2"
if 'match_title' not in st.session_state: st.session_state.match_title = "試合"

# --- 2. カウント処理 (ボタンクリック時に実行) ---
query = st.query_params
if "act" in query:
    p_idx = int(query.get("p", 1))
    item = query.get("i", "")
    is_w = query.get("w") == "1"
    
    st.session_state.history.append((p_idx, item, is_w, list(st.session_state.point_score), list(st.session_state.game_score), list(st.session_state.game_results)))
    target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
    target[item] += 1
    
    if is_w: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        st.session_state.game_results.append(f"{p}-{o}")
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]
    
    st.query_params.clear()
    st.rerun()

# --- 3. デザイン（白背景に黒文字を徹底） ---
st.markdown("""
<style>
    /* 全体を白背景・黒文字に固定 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード */
    .score-box {
        text-align: center; border: 2px solid black; padding: 10px; border-radius: 10px; margin-bottom: 20px;
    }
    
    /* ボタンを絶対横並びにするテーブル */
    table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    
    /* ボタンのデザイン */
    .btn {
        display: block; width: 100%; padding: 15px 0; text-align: center; 
        text-decoration: none; font-weight: bold; font-size: 14px; border-radius: 8px;
        color: white !important; /* ボタンの文字は絶対白 */
    }
    .btn-blue { background-color: #007AFF; } /* 得点用 */
    .btn-red { background-color: #FF3B30; }  /* 失点用 */
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
with st.expander("📝 試合・選手名設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div class="score-box">
    <div style="font-size:14px;">{st.session_state.match_title}</div>
    <div style="font-size:24px; font-weight:bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size:48px; font-weight:bold; color:#007AFF;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

# 操作パネル（Undo）
if st.button("⬅️ Undo (1つ戻る)", use_container_width=True):
    if st.session_state.history:
        p_idx, item, is_w, old_p, old_g, old_gr = st.session_state.history.pop()
        target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
        target[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.divider()

# 選手選択（横並び）
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 強制2列ボタンテーブル ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-weight:bold; padding-bottom:10px;'>入力中: {active_name}</div>", unsafe_allow_html=True)

# テーブル開始
html_content = f"""
<table>
    <tr>
        <th style="background:#007AFF; color:white; border-radius:5px; padding:5px;">得点</th>
        <th style="background:#FF3B30; color:white; border-radius:5px; padding:5px;">失点</th>
    </tr>
"""

for i in range(max(len(items_won), len(items_lost))):
    html_content += "<tr>"
    
    # 得点ボタン
    if i < len(items_won):
        item = items_won[i]
        html_content += f'<td><a href="?act=1&p={p_num}&i={item}&w=1" target="_self" class="btn btn-blue">{item}</a></td>'
    else:
        html_content += "<td></td>"
        
    # 失点ボタン
    if i < len(items_lost):
        item = items_lost[i]
        html_content += f'<td><a href="?act=1&p={p_num}&i={item}&w=0" target="_self" class="btn btn-red">{item}</a></td>'
    else:
        html_content += "<td></td>"
        
    html_content += "</tr>"

html_content += "</table>"
st.markdown(html_content, unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計表示"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_stats.items()), columns=['項目', '回数']))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()
