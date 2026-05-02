import streamlit as st
import pandas as pd

# ページ設定（スマホで見やすく）
st.set_page_config(page_title="ソフトテニス・スコアラー", layout="centered")

# --- 初期設定 ---
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'ノータッチエース', 'ボレー']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス']

if 'p1_stats' not in st.session_state:
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0] # [自ペア, 相手ペア]
    st.session_state.point_score = [0, 0]

# --- ヘッダー・スコア表示 ---
st.title("🎾 Tennis Scorer")

# 大きなスコア表示
col_g1, col_g2 = st.columns(2)
col_g1.metric("GAME", f"{st.session_state.game_score[0]}")
col_g2.metric("GAME (相手)", f"{st.session_state.game_score[1]}")

st.write(f"### 現在のポイント: **{st.session_state.point_score[0]} - {st.session_state.point_score[1]}**")

# --- 記録ボタン ---
def add_point(player, item, is_won):
    if player == 1:
        st.session_state.p1_stats[item] += 1
    else:
        st.session_state.p2_stats[item] += 1
    
    # スコア更新
    if is_won:
        st.session_state.point_score[0] += 1
    else:
        st.session_state.point_score[1] += 1
    
    # 4点先取（2点差）でゲーム
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

st.divider()

# プレイヤー別操作エリア
tab1, tab2 = st.tabs(["Player 1", "Player 2"])

for i, tab in enumerate([tab1, tab2], 1):
    with tab:
        st.write("✅ **得点要因**")
        cols = st.columns(2)
        for idx, item in enumerate(items_won):
            if cols[idx % 2].button(item, key=f"w_{i}_{item}", use_container_width=True):
                add_point(i, item, True)
                st.rerun()

        st.write("❌ **失点要因**")
        cols_l = st.columns(2)
        for idx, item in enumerate(items_lost):
            if cols_l[idx % 2].button(item, key=f"l_{i}_{item}", use_container_width=True):
                add_point(i, item, False)
                st.rerun()

# --- 統計データ ---
st.divider()
if st.expander("📊 試合統計・確率を表示"):
    for name, stats in [("Player 1", st.session_state.p1_stats), ("Player 2", st.session_state.p2_stats)]:
        st.write(f"#### {name}")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = df['回数'].sum()
        df['確率(%)'] = df['回数'].apply(lambda x: round((x / total * 100), 1) if total > 0 else 0)
        st.table(df)

if st.button("リセット"):
    st.session_state.clear()
    st.rerun()
