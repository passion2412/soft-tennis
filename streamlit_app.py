import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# スマホでも横並びを維持し、ボタンをコンパクトにするCSS
st.markdown("""
    <style>
    /* カラムの横並びを維持 */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 50% !important;
    }
    /* ボタンをさらに小さく */
    .stButton button {
        width: 100%;
        padding: 2px 0px !important;
        font-size: 12px !important;
        margin-bottom: 2px !important;
        height: 35px !important;
    }
    /* 全体の余白を削る */
    .block-container {
        padding: 0.5rem 0.5rem !important;
    }
    h1, h2, h3 {
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 初期設定 ---
items_won = ['サービスA', 'レシーブA', 'スマッシュ', 'ノータッチ', 'ボレー', '相手ミス', '相手DF']
items_lost = ['DF', 'レシーブミス', 'スマミス', 'ストミス', 'ボレーミス', '相手エース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]

# --- 試合情報（折りたたみ） ---
with st.expander("試合詳細設定"):
    p1_name = st.text_input("選手1", value="選手1")
    p2_name = st.text_input("選手2", value="選手2")
    match_info = st.text_input("試合名/相手", value="")

# --- スコア表示 ---
st.markdown(f"""
    <div style="text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 8px; margin-bottom: 5px;">
        <h3 style="margin: 0; font-size: 14px;">G: {st.session_state.game_score[0]} — {st.session_state.game_score[1]}</h3>
        <h2 style="margin: 0; color: #ff4b4b;">P: {st.session_state.point_score[0]} — {st.session_state.point_score[1]}</h2>
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

# --- ボタン配置 ---
def render_buttons(p_num, name):
    st.markdown(f"<p style='margin: 0; font-weight: bold; font-size: 14px;'>【{name}】</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.caption("🔵得点")
        for item in items_won:
            if st.button(item, key=f"w{p_num}{item}"):
                add_record(p_num, item, True)
                st.rerun()
    with c2:
        st.caption("🔴失点")
        for item in items_lost:
            if st.button(item, key=f"l{p_num}{item}"):
                add_record(p_num, item, False)
                st.rerun()

render_buttons(1, p1_name)
st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
render_buttons(2, p2_name)

# --- 統計 ---
if st.checkbox("統計表示"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = sum(stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
