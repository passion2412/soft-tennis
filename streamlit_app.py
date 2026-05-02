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

# --- 共通スタイル（CSS） ---
st.markdown("""
    <style>
    /* 全体の余白削除 */
    .block-container { padding: 0.5rem !important; }
    /* ボタンの基本デザイン */
    .stButton button {
        width: 100%;
        height: 45px !important;
        font-size: 13px !important;
        margin: 2px 0px !important;
        border-radius: 5px !important;
    }
    /* 青ボタン（得点） */
    div.win-btn button {
        background-color: #e1f5fe !important;
        border: 1px solid #03a9f4 !important;
        color: #01579b !important;
    }
    /* 赤ボタン（失点） */
    div.loss-btn button {
        background-color: #ffebee !important;
        border: 1px solid #ef5350 !important;
        color: #b71c1c !important;
    }
    /* やり直しボタン */
    div.undo-btn button {
        background-color: #f5f5f5 !important;
        height: 40px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 試合情報（折りたたみ） ---
with st.expander("試合設定"):
    p1_name = st.text_input("選手1", value="選手1")
    p2_name = st.text_input("選手2", value="選手2")

# --- スコア表示 ---
st.markdown(f"""
    <div style="text-align: center; background-color: #333; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
        <div style="font-size: 14px; opacity: 0.8;">GAME</div>
        <div style="font-size: 24px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
        <div style="font-size: 12px; margin-top: 5px; opacity: 0.8;">POINT</div>
        <div style="font-size: 32px; font-weight: bold; color: #ffeb3b;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
    </div>
    """, unsafe_allow_html=True)

# やり直しボタン
st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
if st.button("⬅️ やり直し", use_container_width=True):
    if len(st.session_state.history) > 0:
        last_action = st.session_state.history.pop()
        player, item, is_won, old_point, old_game = last_action
        if player == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score = old_point
        st.session_state.game_score = old_game
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

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

# --- メイン操作エリア（強制横並びレイアウト） ---
def render_player_section(p_num, name):
    st.markdown(f"<div style='margin-top: 15px; font-weight: bold;'>【{name}】</div>", unsafe_allow_html=True)
    
    # 2つのカラムを常に50%ずつに固定する
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="win-btn">', unsafe_allow_html=True)
        st.caption("🔵得点")
        for item in items_won:
            if st.button(item, key=f"w{p_num}{item}"):
                add_record(p_num, item, True)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="loss-btn">', unsafe_allow_html=True)
        st.caption("🔴失点")
        for item in items_lost:
            if st.button(item, key=f"l{p_num}{item}"):
                add_record(p_num, item, False)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

render_player_section(1, p1_name)
st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
render_player_section(2, p2_name)

# --- 統計 ---
st.markdown("---")
if st.checkbox("データを確認"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = sum(stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット"):
    st.session_state.clear()
    st.rerun()
