import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
# 統計に含める自力の項目（相手起因の項目を除外）
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

# 統計データから除外する項目リスト
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.game_results = []  # 各ゲームのスコア履歴
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]
    st.session_state.active_player = 1 

# --- 記録処理 ---
def process_action(p_num, item, is_won):
    st.session_state.history.append((
        p_num, item, is_won, list(st.session_state.point_score), list(st.session_state.game_score), list(st.session_state.game_results)
    ))
    
    # 統計加算
    if p_num == 1: st.session_state.p1_stats[item] += 1
    else: st.session_state.p2_stats[item] += 1
    
    # スコア加算
    if is_won: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    
    # ゲームカウント処理
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        # ゲーム終了時のスコアを記録
        st.session_state.game_results.append(f"{p} — {o}")
        
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
    .btn {
        display: block; width: 100%; height: 48px; line-height: 48px;
        text-align: center; text-decoration: none; border-radius: 8px;
        font-size: 13px; font-weight: bold; color: #FFFFFF !important; 
    }
    .btn-win { background-color: #1976D2; border: 1px solid #1565C0; }
    .btn-loss { background-color: #D32F2F; border: 1px solid #B71C1C; }
    .game-history { background: #f0f2f6; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- メイン表示 ---
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

# ゲーム別スコアの表示
if st.session_state.game_results:
    history_str = " / ".join(st.session_state.game_results)
    st.markdown(f"<div class='game-history'>各ゲームスコア: {history_str}</div>", unsafe_allow_html=True)

# 一つ戻るボタン
if st.button("⬅️ 一つ戻る", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        p_num, item, is_won, old_p, old_g, old_gr = last
        if p_num == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.divider()

# --- 選手切り替え ---
col_sel1, col_sel2 = st.columns(2)
if col_sel1.button(f"👤 {p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if col_sel2.button(f"👤 {p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 操作エリア ---
p_num = st.session_state.active_player
win_html = "".join([f'<a href="?p={p_num}&i={item}&w=1" class="btn btn-win" target="_self">{item}</a>' for item in items_won])
loss_html = "".join([f'<a href="?p={p_num}&i={item}&w=0" class="btn btn-loss" target="_self">{item}</a>' for item in items_lost])

st.markdown(f"""
<div class="flex-container">
    <div class="flex-col">
        <div style="text-align:center; font-weight:bold; color:#1976D2; font-size:12px;">🔵得点</div>
        {win_html}
    </div>
    <div class="flex-col">
        <div style="text-align:center; font-weight:bold; color:#D32F2F; font-size:12px;">🔴失点</div>
        {loss_html}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 統計 ---
st.divider()
if st.checkbox("📊 統計データを確認"):
    st.write(f"**試合:** {match_title}")
    # ゲーム履歴を表形式で表示
    if st.session_state.game_results:
        st.write("**【ゲーム別得点詳細】**")
        st.table(pd.DataFrame([st.session_state.game_results], columns=[f"G{i+1}" for i in range(len(st.session_state.game_results))]))

    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**【{name} 統計】**")
        # 相手起因の項目を除外して表示
        filtered_stats = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered_stats.items()), columns=['項目', '回数'])
        total = sum(filtered_stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット"):
    st.session_state.clear()
    st.rerun()
