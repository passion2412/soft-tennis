import streamlit as st
import pandas as pd

# 1. ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# 2. 初期設定（項目名は完全復元済み）
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'p1_score' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア", 'match_name': "今日の試合"
    })

# 3. カウント関数（ボタン押下時に確実に実行される）
def count_point(item, is_win):
    stats = st.session_state.p1_stats if st.session_state.active_player == 1 else st.session_state.p2_stats
    stats[item] += 1
    
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    # ゲーム判定（4ポイント先取・2点差）
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# 4. CSS（「いい感じ」の表示を完全再現・固定）
st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード */
    .match-title { text-align: center; font-size: 14px; font-weight: bold; color: #555; margin-bottom: 2px; }
    .score-board {
        width: 100%; background: #222; color: white; border-radius: 8px;
        text-align: center; padding: 8px 0; margin-bottom: 10px;
    }

    /* 横並び2列を絶対維持 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; gap: 4px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0 !important; }

    /* ボタンデザイン（表示オッケーと言われたスタイルを標準ボタンに適用） */
    div.stButton > button {
        width: 100% !important; height: 46px !important;
        font-weight: 800 !important; font-size: 11px !important;
        border-radius: 5px !important; border: none !important;
        color: white !important; line-height: 1.1 !important;
        padding: 0 2px !important;
    }
    
    /* 青・赤の塗り分け */
    [data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #007AFF !important; }
    [data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #FF3B30 !important; }

    /* 文字色保護 */
    div.stButton > button p { color: white !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# 5. UI描画
st.markdown(f'<div class="match-title">{st.session_state.match_name}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="score-board">
    <div style="font-size: 12px; opacity: 0.8;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
    <div style="font-size: 36px; font-weight: 900; line-height: 1.2;">
        {st.session_state.p1_score} — {st.session_state.p2_score}
    </div>
    <div style="font-size: 14px; color: #4CAF50;">Game: {st.session_state.p1_games} - {st.session_state.p2_games}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
if c1.button(f"👤 {st.session_state.p1_name}", key="sel_p1"):
    st.session_state.active_player = 1
    st.rerun()
if c2.button(f"👤 {st.session_state.p2_name}", key="sel_p2"):
    st.session_state.active_player = 2
    st.rerun()

cur_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; margin: 5px 0;'>記録中: {cur_name}</div>", unsafe_allow_html=True)

# 6. 入力エリア（標準ボタンをCSSでカスタム化）
for w, l in zip(items_won, items_lost):
    col_w, col_l = st.columns(2)
    col_w.button(w, key=f"btn_w_{w}", on_click=count_point, args=(w, True))
    col_l.button(l, key=f"btn_l_{l}", on_click=count_point, args=(l, False))

# 7. 設定・統計
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("⚙️ 設定 / 📊 統計"):
    st.session_state.match_name = st.text_input("試合名", st.session_state.match_name)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)
    st.divider()
    st.write(f"**{st.session_state.p1_name}**", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**", pd.Series(st.session_state.p2_stats))
    if st.button("全リセット"):
        st.session_state.clear()
        st.rerun()
