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

# --- 3. 必要最小限のCSS（視認性と幅の調整） ---
st.markdown("""
<style>
    /* 文字色を黒に固定 */
    .stApp { color: #31333F; background-color: white; }
    
    /* 画面幅に収める設定 */
    .block-container { padding: 1rem !important; }
    
    /* ボタンの共通スタイル（文字は白、幅は100%） */
    div.stButton > button {
        width: 100% !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 2px !important;
        height: 50px !important;
    }
    
    /* 青ボタン(得点) */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #007AFF !important; }
    /* 赤ボタン(失点) */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #FF3B30 !important; }

    /* スコア表示 */
    .score-board {
        text-align: center; background-color: #f0f2f6; 
        padding: 15px; border-radius: 10px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
with st.expander("📝 名前・試合設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    c_n1, c_n2 = st.columns(2)
    st.session_state.p1_name = c_n1.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = c_n2.text_input("選手2", st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div class="score-board">
    <div style="font-size: 14px; color: #555;">{st.session_state.match_title}</div>
    <div style="font-size: 24px; font-weight: bold; color: black;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 48px; font-weight: bold; color: #007AFF;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.info(f"履歴: {' / '.join(st.session_state.game_results)}")

if st.button("⬅️ Undo (1つ戻る)", use_container_width=True):
    if st.session_state.history:
        p_idx, item, is_w, old_p, old_g, old_gr = st.session_state.history.pop()
        target = st.session_state.p1_stats if p_idx == 1 else st.session_state.p2_stats
        target[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.divider()

# 選手切り替え
sel1, sel2 = st.columns(2)
if sel1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if sel2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 入力セクション (カラムごとにボタンを配置) ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; color:black;'>入力中: {active_name}</p>", unsafe_allow_html=True)

# 2列固定のためのコンテナ
row_header = st.columns(2)
row_header[0].markdown("<div style='text-align:center; background:#007AFF; color:white; border-radius:5px; font-weight:bold;'>🔵 得点</div>", unsafe_allow_html=True)
row_header[1].markdown("<div style='text-align:center; background:#FF3B30; color:white; border-radius:5px; font-weight:bold;'>🔴 失点</div>", unsafe_allow_html=True)

max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    # iPhoneでも横並びを維持する唯一の確実な方法: 毎回 columns を呼び出す
    cols = st.columns(2)
    
    with cols[0]:
        if i < len(items_won):
            it = items_won[i]
            st.button(it, key=f"win_{i}", on_click=add_point, args=(p_num, it, True))
            
    with cols[1]:
        if i < len(items_lost):
            it = items_lost[i]
            st.button(it, key=f"loss_{i}", on_click=add_point, args=(p_num, it, False))

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計表示"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        f_s = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_s.items()), columns=['項目', '回数']))

if st.button("全リセット", use_container_width=True):
    st.session_state.clear()
    st.rerun()
