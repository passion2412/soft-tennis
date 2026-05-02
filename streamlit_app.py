import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'game_results': [], 
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost}, 
        'game_score': [0, 0], 'point_score': [0, 0], 
        'active_player': 1, 'p1_name': "選手1", 'p2_name': "選手2", 'match_title': "試合"
    })

# --- 2. カウント関数 ---
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

# --- 3. CSS（表示を固定しつつボタンをデザイン） ---
st.markdown(f"""
<style>
    .stApp {{ background-color: white; color: black; }}
    
    /* スコアボードのデザイン */
    .score-box {{
        text-align: center; border: 2px solid black; padding: 10px; 
        border-radius: 10px; margin-bottom: 20px; background-color: #f9f9f9;
    }}

    /* ボタンの配置と色付け */
    div.stButton > button {{
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        margin-bottom: -10px !important;
    }}
    
    /* 左列（得点）のボタンを青に */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {{
        background-color: #007AFF !important;
    }}
    
    /* 右列（失点）のボタンを赤に */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {{
        background-color: #FF3B30 !important;
    }}

    /* カラムの隙間と横並び維持 */
    [data-testid="column"] {{
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
with st.expander("📝 試合・選手名設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)

st.markdown(f"""
<div class="score-box">
    <div style="font-size:14px; color:#666;">{st.session_state.match_title}</div>
    <div style="font-size:24px; font-weight:bold; color:black;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
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

# 選手選択（横並び）
sel1, sel2 = st.columns(2)
if sel1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if sel2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 入力セクション（横並び死守 & カウント重視） ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-weight:bold; margin-bottom:10px;'>入力中: {active_name}</div>", unsafe_allow_html=True)

# 見出し
h_col1, h_col2 = st.columns(2)
h_col1.markdown("<div style='text-align:center; background:#007AFF; color:white; border-radius:5px; font-weight:bold; font-size:14px; padding:3px;'>🔵 得点</div>", unsafe_allow_html=True)
h_col2.markdown("<div style='text-align:center; background:#FF3B30; color:white; border-radius:5px; font-weight:bold; font-size:14px; padding:3px;'>🔴 失点</div>", unsafe_allow_html=True)

# ボタンリストを1行ずつ配置（CSSのflex-wrap: nowrapにより横並びを強制）
max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    row_cols = st.columns(2)
    
    with row_cols[0]:
        if i < len(items_won):
            it = items_won[i]
            st.button(it, key=f"w_{i}", on_click=add_point, args=(p_num, it, True))
            
    with row_cols[1]:
        if i < len(items_lost):
            it = items_lost[i]
            st.button(it, key=f"l_{i}", on_click=add_point, args=(p_num, it, False))

# --- 6. 統計 ---
if st.checkbox("📊 統計表示"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_stats.items()), columns=['項目', '回数']))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()

