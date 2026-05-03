import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

for key in ['p1_stats', 'p2_stats', 'game_score', 'point_score', 'history', 'game_results', 'active_player', 'p1_name', 'p2_name', 'match_title']:
    if key not in st.session_state:
        if 'stats' in key: st.session_state[key] = {item: 0 for item in items_won + items_lost}
        elif 'score' in key: st.session_state[key] = [0, 0]
        elif 'results' in key or 'history' in key: st.session_state[key] = []
        elif 'active_player' in key: st.session_state[key] = 1
        elif 'p1_name' in key: st.session_state[key] = "選手1"
        elif 'p2_name' in key: st.session_state[key] = "選手2"
        elif 'match_title' in key: st.session_state[key] = "試合"

# --- 2. カウントロジック (連続クリック対応) ---
query = st.query_params
# "uid"（ユニークID）が新しくなるたびに処理を実行
if "act" in query:
    p_idx = int(query.get("p", 1))
    item = query.get("i", "")
    is_w = query.get("w") == "true"
    
    # 履歴保存
    st.session_state.history.append((p_idx, item, is_w, list(st.session_state.point_score), list(st.session_state.game_score), list(st.session_state.game_results)))
    
    # 統計加算
    target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
    if item in target: target[item] += 1
    
    # スコア加算
    if is_w: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    
    # ゲーム終了判定
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        st.session_state.game_results.append(f"{p}-{o}")
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]
    
    # パラメータをクリアしてリロード
    st.query_params.clear()
    st.rerun()

# --- 3. デザイン（視認性重視） ---
st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    .score-box {
        text-align: center; border: 2px solid black; padding: 10px; 
        border-radius: 10px; background-color: #f9f9f9; color: black; margin-bottom: 15px;
    }
    .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; }
    .btn {
        display: block; text-align: center; padding: 15px 2px; border-radius: 8px;
        text-decoration: none; font-size: 13px; font-weight: bold; color: white !important;
    }
    .btn-blue { background-color: #007AFF; }
    .btn-red { background-color: #FF3B30; }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
with st.expander("📝 名前・試合名設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)

st.markdown(f"""
<div class="score-box">
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

# --- 5. 入力セクション (Gridレイアウト) ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-weight:bold; color:black; margin-bottom:10px;'>入力中: {active_name}</div>", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="grid-container" style="margin-bottom:5px;">
    <div style="background:#007AFF; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold;">得点</div>
    <div style="background:#FF3B30; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold;">失点</div>
</div>
""", unsafe_allow_html=True)

# ボタン生成
html_buttons = '<div class="grid-container">'
for i in range(max(len(items_won), len(items_lost))):
    # 得点側
    if i < len(items_won):
        it = items_won[i]
        rid = random.randint(1, 999999) # 連続クリック対策のランダムID
        html_buttons += f'<a href="?act=1&p={p_num}&i={it}&w=true&uid={rid}" target="_self" class="btn btn-blue">{it}</a>'
    else: html_buttons += "<div></div>"
    
    # 失点側
    if i < len(items_lost):
        it = items_lost[i]
        rid = random.randint(1, 999999)
        html_buttons += f'<a href="?act=1&p={p_num}&i={it}&w=false&uid={rid}" target="_self" class="btn btn-red">{it}</a>'
    else: html_buttons += "<div></div>"

html_buttons += "</div>"
st.markdown(html_buttons, unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_s = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_s.items()), columns=['項目', '回数']))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()
