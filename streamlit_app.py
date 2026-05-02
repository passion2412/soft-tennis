import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="Tennis Score Board", layout="centered")

# --- 1. 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']
exclude_items = ['相手のミス', '相手のダブルフォルト', '相手のエース', '相手のサービスエース']

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.game_results = []
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]
    st.session_state.active_player = 1
    st.session_state.p1_name = "選手1"
    st.session_state.p2_name = "選手2"
    st.session_state.match_title = "Match"

# --- 2. カウント処理関数 (表示を崩さない仕組み) ---
def add_point(p_num, item, is_won):
    # 履歴保存
    st.session_state.history.append((
        p_num, item, is_won, 
        list(st.session_state.point_score), 
        list(st.session_state.game_score), 
        list(st.session_state.game_results)
    ))
    
    # 統計加算
    if p_num == 1: st.session_state.p1_stats[item] += 1
    else: st.session_state.p2_stats[item] += 1
    
    # ポイント加算
    if is_won: st.session_state.point_score[0] += 1
    else: st.session_state.point_score[1] += 1
    
    # ゲーム終了判定
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        st.session_state.game_results.append(f"{p}-{o}")
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

# --- 3. CSS (文字色と横並びの死守) ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    /* ボタンの文字を白に固定 */
    .stButton > button {
        color: white !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 8px !important;
        border: none !important;
    }
    /* スコアボードのデザイン */
    .score-card {
        text-align: center; background: #262626; color: white;
        padding: 15px; border-radius: 12px; border: 1px solid #444; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 入力エリア ---
with st.expander("⚙️ 試合・選手名の設定"):
    st.session_state.match_title = st.text_input("試合名", value=st.session_state.match_title)
    col_n1, col_n2 = st.columns(2)
    st.session_state.p1_name = col_n1.text_input("選手1 名前", value=st.session_state.p1_name)
    st.session_state.p2_name = col_n2.text_input("選手2 名前", value=st.session_state.p2_name)

# スコア表示
st.markdown(f"""
<div class="score-card">
    <div style="font-size: 14px; color: #aaa;">{st.session_state.match_title}</div>
    <div style="font-size: 26px; font-weight: bold; margin: 5px 0;">{st.session_state.game_score[0]} — {st.session_state.game_score[1]}</div>
    <div style="font-size: 48px; font-weight: bold; color: #00FF00;">{st.session_state.point_score[0]} — {st.session_state.point_score[1]}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.game_results:
    st.markdown(f"<div style='text-align:center; font-size:14px; margin-bottom:10px;'>History: {' / '.join(st.session_state.game_results)}</div>", unsafe_allow_html=True)

# 一つ戻るボタン
if st.button("⬅️ Undo (一つ戻る)", use_container_width=True):
    if st.session_state.history:
        last = st.session_state.history.pop()
        p_num, item, is_won, old_p, old_g, old_gr = last
        if p_num == 1: st.session_state.p1_stats[item] -= 1
        else: st.session_state.p2_stats[item] -= 1
        st.session_state.point_score, st.session_state.game_score, st.session_state.game_results = old_p, old_g, old_gr
        st.rerun()

st.write("---")

# 選手切り替え
c_p1, c_p2 = st.columns(2)
if c_p1.button(f"👤 {st.session_state.p1_name}", type="primary" if st.session_state.active_player == 1 else "secondary", use_container_width=True):
    st.session_state.active_player = 1
    st.rerun()
if c_p2.button(f"👤 {st.session_state.p2_name}", type="primary" if st.session_state.active_player == 2 else "secondary", use_container_width=True):
    st.session_state.active_player = 2
    st.rerun()

# --- 5. 横並び入力ボタン (1行ずつ確実に生成) ---
p_num = st.session_state.active_player
active_name = st.session_state.p1_name if p_num == 1 else st.session_state.p2_name

st.markdown(f"<p style='text-align:center; font-weight:bold;'>【{active_name}】の入力を選択</p>", unsafe_allow_html=True)

# 見出し
col_h1, col_h2 = st.columns(2)
col_h1.markdown("<div style='text-align:center; background:#0056b3; color:white; border-radius:5px; padding:5px; font-size:14px;'>🔵 得点</div>", unsafe_allow_html=True)
col_h2.markdown("<div style='text-align:center; background:#c82333; color:white; border-radius:5px; padding:5px; font-size:14px;'>🔴 失点</div>", unsafe_allow_html=True)

# ボタン群
max_rows = max(len(items_won), len(items_lost))
for i in range(max_rows):
    # ここで1行ごとに新しいカラムを作成することで、iPhone縦画面での1列化を防ぎます
    row_col1, row_col2 = st.columns(2)
    
    with row_col1:
        if i < len(items_won):
            item_w = items_won[i]
            # on_clickを使うことで、URLパラメータに頼らず確実にカウント
            st.button(item_w, key=f"win_{i}", on_click=add_point, args=(p_num, item_w, True), use_container_width=True, help="得点")
            st.markdown("<style>div[data-testid='column']:nth-of-type(1) button { background-color: #007bff !important; }</style>", unsafe_allow_html=True)

    with row_col2:
        if i < len(items_lost):
            item_l = items_lost[i]
            st.button(item_l, key=f"loss_{i}", on_click=add_point, args=(p_num, item_l, False), use_container_width=True, help="失点")
            st.markdown("<style>div[data-testid='column']:nth-of-type(2) button { background-color: #dc3545 !important; }</style>", unsafe_allow_html=True)

# --- 6. 統計 ---
st.write("---")
if st.checkbox("📊 統計データを確認"):
    for name, stats in [(st.session_state.p1_name, st.session_state.p1_stats), (st.session_state.p2_name, st.session_state.p2_stats)]:
        st.subheader(f"{name}の自力スタッツ")
        filtered = {k: v for k, v in stats.items() if k not in exclude_items}
        df = pd.DataFrame(list(filtered.items()), columns=['項目', '回数'])
        total = sum(filtered.values())
        df['%'] = df['回数'].apply(lambda x: f"{(x/total*100):.1f}%" if total > 0 else "0%")
        st.table(df)

if st.button("全データをリセット", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.rerun()
