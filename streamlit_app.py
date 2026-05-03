import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="Tennis Score", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手 of the service ace']

for key in ['p1_stats', 'p2_stats', 'game_score', 'point_score', 'history', 'game_results', 'active_player', 'p1_name', 'p2_name', 'match_title']:
    if key not in st.session_state:
        if 'stats' in key: st.session_state[key] = {item: 0 for item in items_won + items_lost}
        elif 'score' in key: st.session_state[key] = [0, 0]
        elif 'results' in key or 'history' in key: st.session_state[key] = []
        elif 'active_player' in key: st.session_state[key] = 1
        elif 'p1_name' in key: st.session_state[key] = "選手1"
        elif 'p2_name' in key: st.session_state[key] = "選手2"
        elif 'match_title' in key: st.session_state[key] = "試合"

# --- 2. カウントロジック ---
def add_point(p_idx, item, is_w):
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

# JavaScriptからの入力を監視
input_data = st.query_params.to_dict()
if "btn_click" in input_data:
    p_idx = int(input_data["p"])
    item = input_data["i"]
    is_w = input_data["w"] == "true"
    add_point(p_idx, item, is_w)
    st.query_params.clear()
    st.rerun()

# --- 3. 画面表示 ---
with st.expander("📝 設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div style="text-align: center; border: 2px solid #333; padding: 10px; border-radius: 10px; background-color: #ffffff; color: black; margin-bottom: 15px;">
    <div style="font-size:14px; color:#666;">{st.session_state.match_title}</div>
    <div style="font-size:24px; font-weight:bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size:48px; font-weight:bold; color:#007AFF;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.button("⬅️ Undo (1つ戻る)", use_container_width=True):
    if st.session_state.history:
        p_idx, item, is_w, old_p, old_g, old_gr = st.session_state.history.pop()
        target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
        target[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.divider()

# 選手選択
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 4. 究極の2列固定HTMLボタン ---
# Streamlitのカラムを使わず、1つのHTML文字列として描画
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name

html_code = f"""
<div style="text-align:center; font-weight:bold; color:black; margin-bottom:10px;">入力中: {active_name}</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%;">
    <div style="background:#007AFF; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:14px;">得点</div>
    <div style="background:#FF3B30; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:14px;">失点</div>
"""

for i in range(max(len(items_won), len(items_lost))):
    # 得点ボタン
    if i < len(items_won):
        it = items_won[i]
        html_code += f'<a href="?btn_click=true&p={p_num}&i={it}&w=true" target="_self" style="display:block; background:#007AFF; color:white; text-align:center; padding:15px 2px; border-radius:8px; text-decoration:none; font-size:12px; font-weight:bold;">{it}</a>'
    else:
        html_code += "<div></div>"
    
    # 失点ボタン
    if i < len(items_lost):
        it = items_lost[i]
        html_code += f'<a href="?btn_click=true&p={p_num}&i={it}&w=false" target="_self" style="display:block; background:#FF3B30; color:white; text-align:center; padding:15px 2px; border-radius:8px; text-decoration:none; font-size:12px; font-weight:bold;">{it}</a>'
    else:
        html_code += "<div></div>"

html_code += "</div>"

# 描画
st.markdown(html_code, unsafe_allow_html=True)

# 統計
st.divider()
if st.checkbox("📊 統計"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_s = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_s.items()), columns=['項目', '回数']))

if st.button("全データリセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()

