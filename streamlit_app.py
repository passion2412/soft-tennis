import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]
    st.session_state.active_player = 1 

# --- 記録処理 ---
def process_action(p_num, item, is_won):
    st.session_state.history.append((
        p_num, item, is_won, list(st.session_state.point_score), list(st.session_state.game_score)
    ))
    if p_num == 1: st.session_state.p1_stats[item] += 1
    else: st.session_state.p2_stats[item] += 1
    
    if is_won: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

# URLパラメータ処理
params = st.query_params
if "p" in params:
    process_action(int(params["p"]), params["i"], params["w"] == "1")
    st.query_params.clear()
    st.rerun()

# --- CSS設定 ---
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; }
    .score-box { text-align: center; background: #1E1E1E; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #444; }
    .flex-container { display: flex; width: 100%; gap: 8px; }
    .flex-col { flex: 1; display: flex; flex-direction: column; gap: 6px; }
    
    /* ボタン共通：文字色を白(#FFFFFF)に固定 */
    .btn {
        display: block; width: 100%; height: 48px; line-height: 48px;
        text-align: center; text-decoration: none; border-radius: 8px;
        font-size: 13px; font-weight: bold;
        color: #FFFFFF !important; 
    }
    /* 得点：濃い青 */
    .btn-win { background-color: #1976D2; border: 1px solid #1565C0; }
    /* 失点：濃い赤 */
    .btn-loss { background-color: #D32F2F; border: 1px solid #B71C1C; }
    
    /* ラベルの文字色調整 */
    .column-label { text-align: center; font-weight: bold; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 試合情報入力 ---
st.title("📋 スコア記録")

with st.expander("📝 選手名・試合情報を入力"):
    match_title = st.text_input("試合名", value="")
    col_names = st.columns(2)
    p1_name = col_names[0].text_input("選手1 名前", value="選手1")
    p2_name = col_names[1].text_input("選手2 名前", value="選手2")

# スコア表示
st.markdown(f"""
<div class="score-box">
    <div style="font-size: 14px; opacity:0.7;">{match_title if match_title else 'MATCH'}</div>
    <div style="font-size: 22px; font-weight: bold;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 36px; color: #FFD700; font-weight: bold;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

# 一つ戻るボタン（名称変更）
if st.button("⬅️ 一つ戻る", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        player, item, is_won, old_p, old_g = last
        if player == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score = old_p, old_g
        st.rerun()

st.divider()

# --- 選手切り替え ---
st.write("▼ 入力する選手を選択")
col_sel1, col_sel2 = st.columns(2)
if col_sel1.button(f"👤 {p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if col_sel2.button(f"👤 {p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 操作エリア ---
p_num = st.session_state.active_player

# 「入力中：選手名」の表示を削除し、直接ボタンエリアへ
win_html = "".join([f'<a href="?p={p_num}&i={item}&w=1" class="btn btn-win" target="_self">{item}</a>' for item in items_won])
loss_html = "".join([f'<a href="?p={p_num}&i={item}&w=0" class="btn btn-loss" target="_self">{item}</a>' for item in items_lost])

st.markdown(f"""
<div class="flex-container">
    <div class="flex-col">
        <div class="column-label" style="color:#1976D2;">🔵得点</div>
        {win_html}
    </div>
    <div class="flex-col">
        <div class="column-label" style="color:#D32F2F;">🔴失点</div>
        {loss_html}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 統計 ---
st.divider()
if st.checkbox("📊 統計データを確認"):
    st.write(f"**試合:** {match_title}")
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**【{name}】**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = sum(stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット"):
    st.session_state.clear()
    st.rerun()
