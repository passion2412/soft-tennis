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

# --- 記録処理用関数 ---
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

# --- クエリパラメータでのボタン反応 ---
params = st.query_params
if "p" in params:
    p_num = int(params["p"])
    item = params["i"]
    is_won = params["w"] == "1"
    process_action(p_num, item, is_won)
    st.query_params.clear()
    st.rerun()

# --- CSS (iPhoneで横並びを絶対維持する) ---
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; }
    .score-box { text-align: center; background: #262730; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    
    /* 2列レイアウトの強制 */
    .flex-container {
        display: flex;
        width: 100%;
        gap: 5px;
        margin-bottom: 5px;
    }
    .flex-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .btn {
        display: block;
        width: 100%;
        height: 40px;
        line-height: 40px;
        text-align: center;
        text-decoration: none;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
    }
    .btn-win { background-color: #E3F2FD; color: #0D47A1; border: 1px solid #2196F3; }
    .btn-loss { background-color: #FFEBEE; color: #B71C1C; border: 1px solid #F44336; }
    .btn-undo { background-color: #f0f0f0; color: black; display: block; width: 100%; text-align: center; padding: 10px; border-radius: 5px; text-decoration: none; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 画面表示 ---
st.title("📋 スコア記録")
p1_name = st.sidebar.text_input("選手1", value="選手1")
p2_name = st.sidebar.text_input("選手2", value="選手2")

st.markdown(f"""
<div class="score-box">
    <div style="font-size: 20px;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 32px; color: #FFEB3B; font-weight: bold;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

# やり直しボタン（HTMLリンク形式）
if st.button("⬅️ やり直し", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        player, item, is_won, old_p, old_g = last
        if player == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score = old_p, old_g
        st.rerun()

# --- 選手別ボタンエリア (HTMLで強制2列) ---
def render_html_buttons(p_num, name):
    st.markdown(f"**【{name}】**")
    
    # 得点ボタン群（左）と失点ボタン群（右）
    win_html = "".join([f'<a href="?p={p_num}&i={item}&w=1" class="btn btn-win" target="_self">{item}</a>' for item in items_won])
    loss_html = "".join([f'<a href="?p={p_num}&i={item}&w=0" class="btn btn-loss" target="_self">{item}</a>' for item in items_lost])
    
    st.markdown(f"""
    <div class="flex-container">
        <div class="flex-col">
            <div style="text-align:center; font-size:10px; color:blue;">🔵得点</div>
            {win_html}
        </div>
        <div class="flex-col">
            <div style="text-align:center; font-size:10px; color:red;">🔴失点</div>
            {loss_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

render_html_buttons(1, p1_name)
st.markdown("<br>", unsafe_allow_html=True)
render_html_buttons(2, p2_name)

# --- 統計 ---
if st.checkbox("統計データ"):
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.write(f"**{name}**")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = sum(stats.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
