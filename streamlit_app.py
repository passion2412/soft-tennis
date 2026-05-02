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

# --- 記録処理関数 ---
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

# --- CSS設定（強制2列グリッド） ---
st.markdown("""
<style>
    /* 全体のマージン削減 */
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* 2列を絶対維持するコンテナ */
    .grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        width: 100%;
    }

    /* ボタンの共通スタイル */
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
        color: white !important;
        border-radius: 8px !important;
        margin: 0 !important;
        font-size: 13px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* 得点ボタン（青） */
    div.win-btn > div.stButton > button {
        background-color: #1976D2 !important;
        border: 1px solid #1565C0 !important;
    }

    /* 失点ボタン（赤） */
    div.loss-btn > div.stButton > button {
        background-color: #D32F2F !important;
        border: 1px solid #B71C1C !important;
    }

    .score-box { text-align: center; background: #1E1E1E; color: white; padding: 10px; border-radius: 10px; border: 2px solid #444; }
    .game-history { background: #f0f2f6; padding: 5px; border-radius: 5px; text-align: center; font-size: 14px; margin: 5px 0; }
    .label { text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 画面構成 ---
st.title("📋 スコア記録")

with st.expander("📝 試合情報を入力"):
    match_title = st.text_input("試合名", value="")
    c1, c2 = st.columns(2)
    p1_name = c1.text_input("選手1", value="選手1")
    p2_name = c2.text_input("選手2", value="選手2")

# スコア表示
st.markdown(f"""
<div class="score-box">
    <div style="font-size: 12px; opacity:0.7;">{match_title if match_title else 'MATCH'}</div>
    <div style="font-size: 20px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 32px; color: #FFD700; font-weight: bold;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.markdown(f"<div class='game-history'>履歴: {' / '.join(st.session_state.game_results)}</div>", unsafe_allow_html=True)

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
sel1, sel2 = st.columns(2)
if sel1.button(f"👤 {p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", key="p1_sel", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if sel2.button(f"👤 {p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", key="p2_sel", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 強制2列レイアウトエリア ---
p_num = st.session_state.active_player

# ラベル部分
st.markdown(f"""
<div class="grid-container">
    <div class="label" style="color:#1976D2;">🔵得点</div>
    <div class="label" style="color:#D32F2F;">🔴失点</div>
</div>
""", unsafe_allow_html=True)

# ボタン部分（最大項目数に合わせてループ）
max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    # CSSのクラスを使ってボタンの色を制御
    col_win, col_loss = st.columns(2)
    
    with col_win:
        if i < len(items_won):
            item = items_won[i]
            st.markdown('<div class="win-btn">', unsafe_allow_html=True)
            st.button(item, key=f"w_{i}", on_click=add_point, args=(p_num, item, True))
            st.markdown('</div>', unsafe_allow_html=True)
            
    with col_right if 'col_right' in locals() else col_loss:
        if i < len(items_lost):
            item = items_lost[i]
            st.markdown('<div class="loss-btn">', unsafe_allow_html=True)
            st.button(item, key=f"l_{i}", on_click=add_point, args=(p_num, item, False))
            st.markdown('</div>', unsafe_allow_html=True)

# --- 統計データ ---
st.divider()
if st.checkbox("📊 統計データを確認"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**【{name} 統計】**")
        filtered_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered_stats.items()), columns=['項目', '回数'])
        total = sum(filtered_stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット"):
    st.session_state.clear()
    st.rerun()
