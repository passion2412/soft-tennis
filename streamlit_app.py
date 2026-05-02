import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

# セッションの初期化
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'game_results': [], 'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost}, 'game_score': [0, 0],
        'point_score': [0, 0], 'active_player': 1, 'p1_name': "選手1",
        'p2_name': "選手2", 'match_title': "試合"
    })

# --- 2. カウント処理関数 ---
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

# --- 3. CSS (横並び固定 & 視認性UP) ---
st.markdown("""
<style>
    /* 画面幅が狭くても2列を維持する魔法 */
    [data-testid="column"] {
        flex: 1 1 calc(50% - 10px) !important;
        min-width: calc(50% - 10px) !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
    }
    /* ボタンのデザイン */
    .stButton > button {
        width: 100% !important;
        height: 60px !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 14px !important;
        margin-bottom: 5px !important;
    }
    /* 青ボタン(得点) */
    div.win-btn button { background-color: #007AFF !important; border: none !important; }
    /* 赤ボタン(失点) */
    div.loss-btn button { background-color: #FF3B30 !important; border: none !important; }
    /* スコアボード(白背景でも見やすいグレー) */
    .score-card {
        text-align: center; background: #f8f9fa; border: 2px solid #333;
        padding: 15px; border-radius: 15px; margin-bottom: 15px;
    }
    .header-label {
        text-align: center; color: white; padding: 5px; border-radius: 5px; font-weight: bold; font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 画面表示 ---
with st.expander("📝 試合設定"):
    st.session_state.match_title = st.text_input("試合名", st.session_state.match_title)
    col_n1, col_n2 = st.columns(2)
    st.session_state.p1_name = col_n1.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = col_n2.text_input("選手2", st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div class="score-card">
    <div style="color: #666; font-size: 14px;">{st.session_state.match_title}</div>
    <div style="font-size: 28px; font-weight: bold; color: #333;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 52px; font-weight: 900; color: #007AFF;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.info(f"履歴: {' / '.join(st.session_state.game_results)}")

# 操作パネル
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

# --- 5. 入力セクション (ここが重要) ---
p_num = st.session_state.active_player
st.markdown(f"<div style='text-align:center; font-weight:bold; margin-bottom:10px;'>入力中: {st.session_state.p1_name if p_num==1 else st.session_state.p2_name}</div>", unsafe_allow_html=True)

# 得点・失点ラベル
l_col, r_col = st.columns(2)
l_col.markdown('<div class="header-label" style="background:#007AFF;">🔵 得点</div>', unsafe_allow_html=True)
r_col.markdown('<div class="header-label" style="background:#FF3B30;">🔴 失点</div>', unsafe_allow_html=True)

# ボタンリスト
max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if i < len(items_won):
            it = items_won[i]
            st.markdown('<div class="win-btn">', unsafe_allow_html=True)
            st.button(it, key=f"w{i}", on_click=add_point, args=(p_num, it, True))
            st.markdown('</div>', unsafe_allow_html=True)
    with b_col2:
        if i < len(items_lost):
            it = items_lost[i]
            st.markdown('<div class="loss-btn">', unsafe_allow_html=True)
            st.button(it, key=f"l{i}", on_click=add_point, args=(p_num, it, False))
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 統計 ---
st.divider()
if st.checkbox("📊 統計を表示"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}のスタッツ**")
        f_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        st.table(pd.DataFrame(list(f_stats.items()), columns=['項目', '回数']))

if st.button("全リセット"):
    st.session_state.clear()
    st.rerun()
