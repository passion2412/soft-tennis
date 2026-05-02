import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="スコア記録", layout="centered")

# --- 初期設定 ---
# 項目名の整理（「要因」を省き、ご要望の項目を追加）
items_won = ['サービスエース', 'レシーブエース', 'スマッシュ', 'ノータッチエース', 'ボレー', '相手のミス', '相手のダブルフォルト']
items_lost = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース']

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = []  # 戻るボタン用の履歴
    st.session_state.p1_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.p2_stats = {item: 0 for item in items_won + items_lost}
    st.session_state.game_score = [0, 0]
    st.session_state.point_score = [0, 0]

# --- 入力エリア（試合情報） ---
st.title("📋 スコア記録")

with st.expander("試合情報を入力", expanded=True):
    match_name = st.text_input("大会名・試合名", placeholder="例：春季大会 1回戦")
    opp_team = st.text_input("対戦相手（ペア名）", placeholder="例：〇〇・△△ペア")
    col_n1, col_n2 = st.columns(2)
    p1_name = col_n1.text_input("選手1の名前", value="プレイヤー1")
    p2_name = col_n2.text_input("選手2の名前", value="プレイヤー2")

# --- スコア表示 ---
st.divider()
c1, c2, c3 = st.columns([1, 2, 1])
c1.metric(f"GAME ({p1_name[:2]}..)", st.session_state.game_score[0])
c3.metric("GAME (相手)", st.session_state.game_score[1])
c2.markdown(f"<h1 style='text-align: center;'>{st.session_state.point_score[0]} - {st.session_state.point_score[1]}</h1>", unsafe_allow_html=True)

# --- 戻るボタン ---
if st.button("⬅️ 1つ前の入力ミスを取り消す", use_container_width=True):
    if len(st.session_state.history) > 0:
        # 最後の操作を復元
        last_action = st.session_state.history.pop()
        player, item, is_won, old_point, old_game = last_action
        
        # 統計を減らす
        if player == 1:
            st.session_state.p1_stats[item] -= 1
        else:
            st.session_state.p2_stats[item] -= 1
        
        # スコアを戻す
        st.session_state.point_score = old_point
        st.session_state.game_score = old_game
        st.rerun()
    else:
        st.warning("これ以上戻れません")

# --- 記録ロジック ---
def add_record(player, item, is_won):
    # 履歴に保存（現在のスコア状態を保存）
    current_state = (
        player, item, is_won, 
        list(st.session_state.point_score), 
        list(st.session_state.game_score)
    )
    st.session_state.history.append(current_state)

    # 統計加算
    if player == 1:
        st.session_state.p1_stats[item] += 1
    else:
        st.session_state.p2_stats[item] += 1
    
    # スコア加算
    if is_won:
        st.session_state.point_score[0] += 1
    else:
        st.session_state.point_score[1] += 1
    
    # ゲームカウント処理
    p, o = st.session_state.point_score
    if (p >= 4 or o >= 4) and abs(p - o) >= 2:
        if p > o: st.session_state.game_score[0] += 1
        else: st.session_state.game_score[1] += 1
        st.session_state.point_score = [0, 0]

st.divider()

# --- 操作エリア ---
tab1, tab2 = st.tabs([p1_name, p2_name])

for i, (tab, name) in enumerate(zip([tab1, tab2], [p1_name, p2_name]), 1):
    with tab:
        st.write(f"🔵 **{name} の得点**")
        cols = st.columns(2)
        for idx, item in enumerate(items_won):
            if cols[idx % 2].button(item, key=f"w_{i}_{item}", use_container_width=True):
                add_record(i, item, True)
                st.rerun()

        st.write(f"🔴 **{name} の失点**")
        cols_l = st.columns(2)
        for idx, item in enumerate(items_lost):
            if cols_l[idx % 2].button(item, key=f"l_{i}_{item}", use_container_width=True):
                add_record(i, item, False)
                st.rerun()

# --- 統計・出力 ---
st.divider()
if st.expander("📊 分析・確率データ"):
    st.write(f"**試合:** {match_name} / **相手:** {opp_team}")
    for name, stats in [(p1_name, st.session_state.p1_stats), (p2_name, st.session_state.p2_stats)]:
        st.subheader(f"分析: {name}")
        df = pd.DataFrame(list(stats.items()), columns=['項目', '回数'])
        total = df['回数'].sum()
        df['確率(%)'] = df['回数'].apply(lambda x: round((x / total * 100), 1) if total > 0 else 0)
        st.table(df)

if st.button("全データをリセット"):
    if st.confirm("本当にリセットしますか？"):
        st.session_state.clear()
        st.rerun()
