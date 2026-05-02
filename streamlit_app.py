import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Score", layout="centered")

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
if 'match_title' not in st.session_state: st.session_state.match_title = "Match"

# --- 2. カウント処理 (クエリパラメータ経由) ---
# ページ最上部でリクエストをキャッチして処理
query = st.query_params
if "act" in query:
    p_idx = int(query.get("p", 1))
    item = query.get("i", "")
    is_w = query.get("w") == "1"
    
    # 履歴保存
    st.session_state.history.append((p_idx, item, is_w, list(st.session_state.point_score), list(st.session_state.game_score), list(st.session_state.game_results)))
    
    # 統計
    target_stats = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
    if item in target_stats: target_stats[item] += 1
    
    # スコア
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

# --- 3. デザインCSS ---
st.markdown(f"""
<style>
    .reportview-container .main .block-container {{ padding-top: 1rem; }}
    .stApp {{ background-color: #0e1117; }}
    .score-card {{
        text-align: center; background: #1a1c23; color: white;
        padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 20px;
    }}
    /* HTMLボタンのスタイル */
    .btn {{
        display: block; text-decoration: none; text-align: center;
        color: white !important; font-weight: bold; padding: 15px 5px;
        border-radius: 10px; font-size: 13px; margin: 2px;
    }}
    .btn-win {{ background-color: #007bff; border-bottom: 4px solid #0056b3; }}
    .btn-loss {{ background-color: #dc3545; border-bottom: 4px solid #a71d2a; }}
    .btn:active {{ transform: translateY(2px); border-bottom: none; }}
</style>
""", unsafe_allow_html=True)

# --- 4. 試合設定エリア ---
with st.expander("⚙️ 名前・試合設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    st.session_state.p1_name = st.text_input("選手1 (左)", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2 (右)", st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div class="score-card">
    <div style="font-size: 14px; color: #888; margin-bottom: 5px;">{st.session_state.match_title}</div>
    <div style="font-size: 28px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 56px; font-weight: bold; color: #00ff00; line-height: 1;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

# 操作パネル
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("⬅️ Undo (1つ戻る)", use_container_width=True):
        if st.session_state.history:
            last = st.session_state.history.pop()
            p_idx, item, is_w, old_p, old_g, old_gr = last
            target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
            target[item] -= 1
            st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
            st.rerun()

st.write("---")

# 選手選択
sel1, sel2 = st.columns(2)
if sel1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if sel2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 強制横並びHTMLテーブル ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name

# ヘッダーとボタンをテーブル構造で描画
html_code = f"""
<div style="text-align:center; margin-bottom:10px; font-weight:bold; color:#ccc;">入力中: {active_name}</div>
<table style="width:100%; border-spacing: 5px; table-layout: fixed;">
    <tr>
        <th style="background:#0056b3; color:white; border-radius:5px; padding:8px; font-size:14px;">🔵 得点</th>
        <th style="background:#a71d2a; color:white; border-radius:5px; padding:8px; font-size:14px;">🔴 失点</th>
    </tr>
"""

for i in range(max(len(items_won), len(items_lost))):
    html_code += "<tr>"
    # 得点ボタン
    if i < len(items_won):
        it = items_won[i]
        html_code += f'<td><a href="?act=1&p={p_num}&i={it}&w=1" target="_self" class="btn btn-win">{it}</a></td>'
    else: html_code += "<td></td>"
    
    # 失点ボタン
    if i < len(items_lost):
        it = items_lost[i]
        html_code += f'<td><a href="?act=1&p={p_num}&i={it}&w=0" target="_self" class="btn btn-loss">{it}</a></td>'
    else: html_code += "<td></td>"
    html_code += "</tr>"

html_code += "</table>"
st.markdown(html_code, unsafe_allow_html=True)

# 統計
st.write("---")
if st.checkbox("📊 統計を表示"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(f_stats.items()), columns=['項目', '回数'])
        st.table(df)

if st.button("全リセット"):
    st.session_state.clear()
    st.rerun()
