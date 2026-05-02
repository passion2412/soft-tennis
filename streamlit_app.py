import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手 of ダブルフォルト', '相手のエース', '相手のサービスエース']

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

# --- CSS（強制レイアウト & 視認性確保） ---
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* ボタンの基本スタイル */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 13px !important;
        color: #FFFFFF !important; /* 絶対に白文字 */
        border: none !important;
    }

    /* 青ボタン（得点）の背景 */
    div.win-zone .stButton > button {
        background-color: #0056b3 !important;
        box-shadow: 0 4px #003d80;
    }

    /* 赤ボタン（失点）の背景 */
    div.loss-zone .stButton > button {
        background-color: #c82333 !important;
        box-shadow: 0 4px #a71d2a;
    }
    
    /* スコアボード */
    .score-card {
        text-align: center; background: #1E1E1E; color: white;
        padding: 15px; border-radius: 10px; border: 2px solid #ffd700; margin-bottom: 10px;
    }

    /* 2列を絶対に崩さないグリッドコンテナ */
    .force-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        column-gap: 10px;
        row-gap: 8px;
        width: 100%;
    }
    .header-label {
        text-align: center; font-weight: bold; font-size: 16px; padding: 5px; border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 画面構成 ---
st.title("🎾 スコア入力")

with st.expander("📝 試合設定"):
    match_title = st.text_input("試合名", value="練習試合")
    p1_name = st.text_input("選手1", value="自分")
    p2_name = st.text_input("選手2", value="相手")

# スコア表示
st.markdown(f"""
<div class="score-card">
    <div style="font-size: 12px; opacity:0.8;">{match_title}</div>
    <div style="font-size: 24px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 42px; font-weight: bold; color: #ffd700;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.info(f"履歴: {' / '.join(st.session_state.game_results)}")

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
c1, c2 = st.columns(2)
if c1.button(f"👤 {p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 操作エリア（CSS Gridによる強制2列表示） ---
p_num = st.session_state.active_player
st.markdown(f"### 入力中: {p1_name if p_num == 1 else p2_name}")

# ヘッダー（得点・失点の分別を明示）
st.markdown("""
<div class="force-grid">
    <div class="header-label" style="background-color:#0056b3; color:white;">🔵 得点</div>
    <div class="header-label" style="background-color:#c82333; color:white;">🔴 失点</div>
</div>
""", unsafe_allow_html=True)

# ボタンリストを1行ずつ配置
max_rows = max(len(items_won), len(items_lost))

for i in range(max_rows):
    # ここで強制的に2つのコンテナを横に並べる
    st.markdown('<div class="force-grid">', unsafe_allow_html=True)
    
    # 左側：得点
    col_win, col_loss = st.columns(2)
    with col_win:
        if i < len(items_won):
            item = items_won[i]
            st.markdown('<div class="win-zone">', unsafe_allow_html=True)
            st.button(item, key=f"win_{i}", on_click=add_point, args=(p_num, item, True))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 右側：失点
    with col_loss:
        if i < len(items_lost):
            item = items_lost[i]
            st.markdown('<div class="loss-zone">', unsafe_allow_html=True)
            st.button(item, key=f"loss_{i}", on_click=add_point, args=(p_num, item, False))
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 統計 ---
st.divider()
if st.checkbox("📊 統計を確認"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.subheader(f"{name}の統計")
        filtered = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered.items()), columns=['項目', '回数'])
        total = sum(filtered.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
