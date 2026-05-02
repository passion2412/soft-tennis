import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# CSSでボタンの隙間や余白を極限まで削るカスタム
st.markdown("""
    <style>
    .stButton button {
        padding: 5px 2px !important;
        font-size: 14px !important;
        margin-bottom: -10px !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    div[data-testid="column"] {
        padding: 0px 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'ノータッチ', 'ボレー', '相手ミス', '相手DF']
items_lost = ['DF', 'レシーブミス', 'スマミス', 'ストミス', 'ボレーミス', '相手エース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]

# --- メイン画面 ---
st.title("📋 スコア記録")

# 試合情報入力（最初だけ表示されるよう折りたたみ）
with st.expander("試合詳細設定"):
    match_name = st.text_input("大会名", placeholder="〇〇大会")
    opp_team = st.text_input("対戦相手", placeholder="〇〇ペア")
    col_n1, col_n2 = st.columns(2)
    p1_name = col_n1.text_input("選手1", value="選手1")
    p2_name = col_n2.text_input("選手2", value="選手2")

# --- スコア表示エリア ---
# ゲーム数の下にポイントを表示
st.markdown(f"""
    <div style="text-align: center; background-color: #f0f2f6; padding: 10px; border-radius: 10px;">
        <p style="margin: 0; font-size: 16px; color: #555;">GAME COUNT</p>
        <h2 style="margin: 0;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</h2>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #555;">POINTS</p>
        <h1 style="margin: 0; color: #ff4b4b;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</h1>
    </div>
    """, unsafe_allow_html=True)

# 戻るボタンを「やり直し」に変更
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
    
    p, o = st.session_score = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

st.markdown("---")

# --- 操作エリア（スクロールなしで1画面に収めるための2カラム×2レイアウト） ---
# 選手をタブではなく上下に並べ、さらに「得点」「失点」を横に並べる
def render_player_buttons(player_num, name):
    st.markdown(f"**【{name}】**")
    win_col, loss_col = st.columns(2)
    with win_col:
        for item in items_won:
            if st.button(f"✨{item}", key=f"w{player_num}{item}", use_container_width=True):
                add_record(player_num, item, True)
                st.rerun()
    with loss_col:
        for item in items_lost:
            if st.button(f"×{item}", key=f"l{player_num}{item}", use_container_width=True):
                add_record(player_num, item, False)
                st.rerun()

# 選手1と選手2をコンパクトに表示
render_player_buttons(1, p1_name)
st.markdown("<div style='margin: 10px;'></div>", unsafe_allow_html=True)
render_player_buttons(2, p2_name)

# --- 統計データ ---
st.markdown("---")
if st.checkbox("📊 統計データ表示"):
    st.write(f"**試合:** {match_name} / **相手:** {opp_team}")
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = df['回数'].sum()
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.dataframe(df, hide_index=True, use_container_width=True)

if st.button("全データをリセット", type="primary"):
    st.session_state.clear()
    st.rerun()
