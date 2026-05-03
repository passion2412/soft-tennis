import streamlit as st
import pandas as pd

# 1. ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# 2. 初期設定（項目名完全復元）
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'p1_score' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア", 'match_name': "今日の試合"
    })

# 3. 超軽量・確実なカウントロジック
# 標準のst.buttonを「見た目だけ」CSSで完全に作り変える
def add(item, win):
    stats = st.session_state.p1_stats if st.session_state.active_player == 1 else st.session_state.p2_stats
    stats[item] += 1
    if win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# 4. CSS（「完璧な表示」を再現しつつ、崩れを物理的に阻止）
st.markdown("""
<style>
    /* 全体設定 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード：高さ固定で崩れ防止 */
    .sb {
        width: 100%; background: #222; color: white; border-radius: 8px;
        text-align: center; padding: 10px 0; margin-bottom: 10px;
    }

    /* 2列を絶対死守するコンテナ */
    [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; gap: 4px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0 !important; }

    /* ボタン：iPhoneの文字消え・崩れを徹底排除 */
    div.stButton > button {
        width: 100% !important;
        height: 44px !important;
        padding: 0 2px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        word-break: break-all !important; /* 長い単語を強制改行して収める */
    }

    /* 文字色を「絶対」に見せるための指定 */
    div.stButton > button p {
        color: white !important; 
        font-size: 11px !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }
    
    /* 得点(青)・失点(赤) */
    [data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #007AFF !important; }
    [data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #FF3B30 !important; }

    /* 余計な余白をカット */
    .block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# 5. UI（表示オッケーと言われたシンプル構成）
st.markdown(f'<div style="text-align:center; font-size:12px; color:#666;">{st.session_state.match_name}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="sb">
    <div style="font-size: 11px; opacity: 0.8;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
    <div style="font-size: 32px; font-weight: 900;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 13px; color: #4CAF50;">Game: {st.session_state.p1_games} - {st.session_state.p2_games}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
c1.button(f"👤 {st.session_state.p1_name}", key="p1btn", on_click=lambda: st.session_state.update(active_player=1))
c2.button(f"👤 {st.session_state.p2_name}", key="p2btn", on_click=lambda: st.session_state.update(active_player=2))

active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; margin: 5px 0;'>記録中: {active_name}</div>", unsafe_allow_html=True)

# 6. メインカウンター
for w, l in zip(items_won, items_lost):
    col1, col2 = st.columns(2)
    col1.button(w, key=f"w_{w}", on_click=add, args=(w, True))
    col2.button(l, key=f"l_{l}", on_click=add, args=(l, False))

# 7. 設定・統計
with st.expander("⚙️ 設定 / 📊 統計"):
    st.session_state.match_name = st.text_input("試合名", st.session_state.match_name)
    st.session_state.p1_name = st.text_input("選手1", st.session_state.p1_name)
    st.session_state.p2_name = st.text_input("選手2", st.session_state.p2_name)
    st.divider()
    st.write(f"**{st.session_state.p1_name}**統計", pd.Series(st.session_state.p1_stats))
    st.write(f"**{st.session_state.p2_name}**統計", pd.Series(st.session_state.p2_stats))
    if st.button("リセット"):
        st.session_state.clear()
        st.rerun()
