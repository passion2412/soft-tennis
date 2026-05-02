import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
items_won = ['サービスA', 'レシーブA', 'スマッシュ', 'ノータッチ', 'ボレー', '相手ミス', '相手DF']
items_lost = ['DF', 'レシーブミス', 'スマミス', 'ストミス', 'ボレーミス', '相手エース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]

# --- 強制2列レイアウト用のCSS ---
st.markdown("""
    <style>
    /* 画面全体の余白を最小化 */
    .block-container { padding: 0.5rem !important; }
    
    /* 2列のグリッドコンテナ */
    .button-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        width: 100%;
    }

    /* ボタンのスタイル調整 */
    .stButton button {
        width: 100%;
        height: 42px !important;
        font-size: 12px !important;
        padding: 0 !important;
        border-radius: 4px !important;
    }
    
    /* 得点側（左）のボタン色 */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton button {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        color: #0D47A1;
    }
    /* 失点側（右）のボタン色 */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stButton button {
        background-color: #FFEBEE;
        border: 1px solid #F44336;
        color: #B71C1C;
    }
    
    /* スコアボード */
    .scoreboard {
        text-align: center;
        background-color: #262730;
        color: white;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 試合設定 ---
with st.expander("設定"):
    p1_name = st.text_input("選手1", value="選手1")
    p2_name = st.text_input("選手2", value="選手2")

# --- スコア表示 ---
st.markdown(f"""
    <div class="scoreboard">
        <div style="font-size: 12px; opacity: 0.8;">GAME / POINT</div>
        <div style="font-size: 20px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
        <div style="font-size: 32px; font-weight: bold; color: #FFEB3B;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
    </div>
    """, unsafe_allow_html=True)

# やり直しボタン
if st.button("⬅️ やり直し", use_container_width=True):
    if len(st.session_state.history) > 0:
        last_action = st.session_state.history.pop()
        player, item, is_won, old_point, old_game = last_action
        if player == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score = old_point
        st.session_state.game_score = old_game
        st.rerun()

# --- 記録ロジック ---
def add_record(player, item, is_won):
    st.session_state.history.append((
        player, item, is_won, list(st.session_state.point_score), list(st.session_state.game_score)
    ))
    if player == 1: st.session_state.p1_stats[item] += 1
    else: st.session_state.p2_stats[item] += 1
    if is_won: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

# --- 操作ボタンエリア（ここが重要！） ---
def render_player(p_num, name):
    st.write(f"**{name}**")
    # 外枠を2列のコンテナのように見せるため、カラムを作成し、
    # 各カラムの中にボタンを縦に並べる（これで事実上の2列になる）
    left, right = st.columns(2, gap="small")
    
    with left:
        st.caption("🔵得点")
        for item in items_won:
            if st.button(item, key=f"w{p_num}{item}"):
                add_record(p_num, item, True)
                st.rerun()
                
    with right:
        st.caption("🔴失点")
        for item in items_lost:
            if st.button(item, key=f"l{p_num}{item}"):
                add_record(p_num, item, False)
                st.rerun()

render_player(1, p1_name)
st.markdown("---")
render_player(2, p2_name)

# --- 統計 ---
if st.checkbox("データ表示"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = sum(stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
