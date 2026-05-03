import streamlit as st
import pandas as pd

# 1. ページ設定
st.set_page_config(page_title="Tennis Counter", layout="centered")

# 2. 初期設定
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース']

if 'p1_score' not in st.session_state:
    st.session_state.update({
        'p1_score': 0, 'p2_score': 0, 'p1_games': 0, 'p2_games': 0,
        'p1_stats': {i: 0 for i in items_won + items_lost},
        'p2_stats': {i: 0 for i in items_won + items_lost},
        'active_player': 1, 'p1_name': "自分", 'p2_name': "ペア", 'match_name': "今日の試合"
    })

# 3. カウント関数
def count_point(item, is_win):
    stats = st.session_state.p1_stats if st.session_state.active_player == 1 else st.session_state.p2_stats
    stats[item] += 1
    if is_win: st.session_state.p1_score += 1
    else: st.session_state.p2_score += 1
    p1, p2 = st.session_state.p1_score, st.session_state.p2_score
    if (p1 >= 4 or p2 >= 4) and abs(p1 - p2) >= 2:
        if p1 > p2: st.session_state.p1_games += 1
        else: st.session_state.p2_games += 1
        st.session_state.p1_score, st.session_state.p2_score = 0, 0

# 4. CSS（究極の表示死守設定）
st.markdown("""
<style>
    /* 全体背景を白、文字を黒に固定 */
    .stApp { background-color: white !important; color: black !important; }
    
    /* スコアボード */
    .score-board {
        width: 100%; background: #222; color: white; border-radius: 8px;
        text-align: center; padding: 10px 0; margin-bottom: 10px;
    }

    /* 2列グリッドを強制（iPhoneの自動調整を無視） */
    .grid-container {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 4px; width: 100%; position: relative;
    }

    /* ボタンの土台（HTMLで描画するから文字が消えない） */
    .btn-base {
        display: flex; align-items: center; justify-content: center;
        height: 44px; border-radius: 5px; font-size: 11.5px;
        font-weight: 800; color: white !important; text-align: center;
        line-height: 1.1; pointer-events: none; /* 下のボタンにクリックを通す */
    }
    .w-color { background-color: #007AFF; }
    .l-color { background-color: #FF3B30; }

    /* 重ねる本物のボタンを透明化 */
    div.stButton { position: absolute; width: 100%; height: 100%; top: 0; left: 0; opacity: 0; }
    div.stButton > button { width: 100% !important; height: 44px !important; border: none !important; }

    /* カラムの相対位置固定 */
    [data-testid="column"] { position: relative; min-width: 0 !important; flex: 1 !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; gap: 4px !important; }
</style>
""", unsafe_allow_html=True)

# 5. UI描画
st.markdown(f'<div style="text-align:center; font-size:14px; font-weight:bold; color:#555;">{st.session_state.match_name}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="score-board">
    <div style="font-size: 12px; opacity: 0.8;">{st.session_state.p1_name} & {st.session_state.p2_name}</div>
    <div style="font-size: 38px; font-weight: 900; line-height: 1;">{st.session_state.p1_score} — {st.session_state.p2_score}</div>
    <div style="font-size: 14px; color: #4CAF50; margin-top: 4px;">Game: {st.session_state.p1_games} - {st.session_state.p2_games}</div>
</div>
""", unsafe_allow_html=True)

# 選手選択
c1, c2 = st.columns(2)
with c1: st.button(st.session_state.p1_name, key="p1_sel")
with c2: st.button(st.session_state.p2_name, key="p2_sel")
# 簡易的な選手切り替え（透明ボタン方式だと複雑になるため標準を使用）
if st.session_state.get("p1_sel"): st.session_state.active_player = 1
if st.session_state.get("p2_sel"): st.session_state.active_player = 2

active_name = st.session_state.p1_name if st.session_state.active_player == 1 else st.session_state.p2_name
st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:13px;'>記録中: {active_name}</p>", unsafe_allow_html=True)

# 6. 入力パネル（HTMLの見た目 + 透明なボタンの融合）
for w, l in zip(items_won, items_lost):
    col_w, col_l = st.columns(2)
    with col_w:
        # 見た目（HTML）
        st.markdown(f'<div class="btn-base w-color">{w}</div>', unsafe_allow_html=True)
        # 実行（透明ボタン）
        st.button("", key=f"re_w_{w}", on_click=count_point, args=(w, True))
    with col_l:
        # 見た目（HTML）
        st.markdown(f'<div class="btn-base l-color">{l}</div>', unsafe_allow_html=True)
        # 実行（透明ボタン）
        st.button("", key=f"re_l_{l}", on_click=count_point, args=(l, False))

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
