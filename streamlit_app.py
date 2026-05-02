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

# --- CSS（スマホ強制2列 & 色の固定） ---
st.markdown("""
<style>
    /* 1. どんな環境でも1列にさせない設定 */
    [data-testid="column"] {
        flex: 1 1 50% !important;
        width: 50% !important;
        min-width: 50% !important;
    }
    /* 2. ボタンの文字色と背景色を強制固定（白飛び防止） */
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 13px !important;
        margin-bottom: 2px !important;
    }
    /* 得点ボタン：濃い青背景に絶対白文字 */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border: 2px solid #004085 !important;
    }
    /* 失点ボタン：濃い赤背景に絶対白文字 */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background-color: #c82333 !important;
        color: #ffffff !important;
        border: 2px solid #a71d2a !important;
    }
    /* スコア表示 */
    .score-card {
        text-align: center;
        background: #222222;
        color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #ffd700;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- メイン画面 ---
st.title("📋 スコア記録")

with st.expander("📝 試合設定"):
    match_title = st.text_input("試合名", value="")
    p1_name = st.text_input("選手1 名前", value="選手1")
    p2_name = st.text_input("選手2 名前", value="選手2")

# スコア表示
st.markdown(f"""
<div class="score-card">
    <div style="font-size: 14px;">{match_title}</div>
    <div style="font-size: 24px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 40px; font-weight: bold; color: #ffd700;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.info(f"ゲーム履歴: {' / '.join(st.session_state.game_results)}")

if st.button("⬅️ 一つ戻る", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        p_num, item, is_won, old_p, old_g, old_gr = last
        if p_num == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.divider()

# 選手切り替え
c_sel1, c_sel2 = st.columns(2)
if c_sel1.button(f"👤 {p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c_sel2.button(f"👤 {p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- ボタン操作エリア（ここを1行ずつのカラムにして強制並びを実現） ---
p_num = st.session_state.active_player
st.markdown(f"**【{p1_name if p_num == 1 else p2_name}】の入力**")

max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    col1, col2 = st.columns(2) # 1行ごとに2列作る
    
    with col1:
        if i < len(items_won):
            item_w = items_won[i]
            st.button(item_w, key=f"win_{i}", on_click=add_point, args=(p_num, item_w, True))
    
    with col2:
        if i < len(items_lost):
            item_l = items_lost[i]
            st.button(item_l, key=f"loss_{i}", on_click=add_point, args=(p_num, item_l, False))

# --- 統計 ---
st.divider()
if st.checkbox("📊 統計を確認"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        filtered = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered.items()), columns=['項目', '回数'])
        total = sum(filtered.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
