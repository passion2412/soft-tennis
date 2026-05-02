import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.game_results = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]
    st.session_state.active_player = 1 

# --- 記録処理 ---
def add_point(p_num, item, is_won):
    st.session_state.history.append((
        p_num, item, is_won, 
        list(st.session_state.point_score), 
        list(st.session_state.game_score), 
        list(st.session_state.game_results)
    ))
    if p_num == 1: st.session_state.p1_stats[item] += 1
    else: st.session_state.p2_stats[item] += 1
    if is_won: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        st.session_state.game_results.append(f"{p}-{o}")
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

# --- メイン表示 ---
st.title("🎾 スコア入力")

# スコア表示（HTMLで直接記述し、視認性を確保）
st.markdown(f"""
<div style="text-align: center; background: #333; color: white; padding: 15px; border-radius: 10px; border: 2px solid #ffd700;">
    <div style="font-size: 20px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 45px; font-weight: bold; color: #ffd700;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.info(f"ゲーム履歴: {' / '.join(st.session_state.game_results)}")

# URLパラメータによるボタン動作の受け取り
params = st.query_params
if "action" in params:
    add_point(int(params["p"]), params["i"], params["w"] == "1")
    st.query_params.clear()
    st.rerun()

# 選手切り替え
st.write("---")
c1, c2 = st.columns(2)
if c1.button("👤 選手1", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button("👤 選手2", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 強制2列テーブル（ここが肝です） ---
p_num = st.session_state.active_player
st.markdown(f"### 入力中: 選手{p_num}")

# HTMLテーブルでボタンを作成（リンク方式にすることで確実に2列を維持）
html_table = f"""
<table style="width:100%; border-collapse: separate; border-spacing: 8px;">
    <tr>
        <th style="width:50%; background-color:#0056b3; color:white; padding:10px; border-radius:5px;">🔵 得点</th>
        <th style="width:50%; background-color:#c82333; color:white; padding:10px; border-radius:5px;">🔴 失点</th>
    </tr>
"""

max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    html_table += "<tr>"
    # 得点側
    if i < len(items_won):
        item = items_won[i]
        html_table += f'<td style="width:50%;"><a href="?action=1&p={p_num}&i={item}&w=1" target="_self" style="display:block; text-align:center; background-color:#007bff; color:white; padding:15px 5px; text-decoration:none; font-weight:bold; border-radius:8px; font-size:13px; border-bottom:3px solid #0056b3;">{item}</a></td>'
    else:
        html_table += "<td></td>"
    
    # 失点側
    if i < len(items_lost):
        item = items_lost[i]
        html_table += f'<td style="width:50%;"><a href="?action=1&p={p_num}&i={item}&w=0" target="_self" style="display:block; text-align:center; background-color:#dc3545; color:white; padding:15px 5px; text-decoration:none; font-weight:bold; border-radius:8px; font-size:13px; border-bottom:3px solid #a71d2a;">{item}</a></td>'
    else:
        html_table += "<td></td>"
    html_table += "</tr>"

html_table += "</table>"

# HTMLを画面に流し込む
st.markdown(html_table, unsafe_allow_html=True)

# 戻るボタン
if st.button("⬅️ 一つ戻る (Undo)", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        p_num, item, is_won, old_p, old_g, old_gr = last
        if p_num == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

# --- 統計 ---
st.write("---")
if st.checkbox("📊 統計を確認"):
    for name, stats in [("選手1", st.session_state.p1_stats), ("選手2", st.session_state.p2_stats)]:
        st.subheader(f"{name}の自力スタッツ")
        filtered = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered.items()), columns=['項目', '回数'])
        total = sum(filtered.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット"):
    st.session_state.clear()
    st.rerun()
