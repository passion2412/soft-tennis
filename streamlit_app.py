import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="Tennis Stats", layout="centered")

# HTML完全版（タイトル削除 ＆ 統計項目修正）
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, sans-serif; background-color: white; color: black; margin: 0; padding: 5px; }
        .match-name { text-align: center; font-size: 14px; margin-bottom: 5px; color: #666; font-weight: bold; }
        
        /* スコアボード */
        .score-box { background: #222; color: white; border-radius: 12px; text-align: center; padding: 12px; margin-bottom: 12px; }
        .pair-names { font-size: 12px; opacity: 0.8; margin-bottom: 3px; }
        .main-score { font-size: 46px; font-weight: 900; line-height: 1; margin: 8px 0; }
        .game-score { font-size: 14px; color: #4CAF50; font-weight: bold; }

        /* 選手選択 */
        .player-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
        .p-btn { border: 2px solid #007AFF; background: white; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; font-size: 13px; }
        .p-btn.active { background: #007AFF; color: white; }

        .active-label { text-align: center; font-size: 12px; font-weight: bold; margin: 8px 0; border-bottom: 1px solid #eee; padding-bottom: 4px; }

        /* カウンターボタン */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
        .btn { 
            height: 48px; border-radius: 5px; display: flex; align-items: center; justify-content: center; 
            color: white !important; font-weight: bold; font-size: 11.5px; text-align: center; line-height: 1.1;
            cursor: pointer; -webkit-tap-highlight-color: transparent; border: none;
        }
        .btn-win { background-color: #007AFF; }
        .btn-loss { background-color: #FF3B30; }
        .btn:active { opacity: 0.6; transform: scale(0.96); }

        .header { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 4px; text-align: center; font-size: 11px; font-weight: bold; }
        
        /* 下部設定 */
        .footer { margin-top: 20px; border-top: 1px solid #ddd; padding-top: 10px; }
        summary { font-size: 13px; color: #555; padding: 5px; cursor: pointer; }
        input { width: 100%; padding: 8px; margin: 4px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 6px; text-align: center; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>

    <div id="match-display" class="match-name">今日の試合</div>

    <div class="score-box">
        <div id="names-display" class="pair-names">自分 & ペア</div>
        <div id="points" class="main-score">0 — 0</div>
        <div id="games" class="game-score">Game: 0 — 0</div>
    </div>

    <div class="player-selector">
        <div id="p1-tag" class="p-btn active" onclick="setPlayer(1)">自分</div>
        <div id="p2-tag" class="p-btn" onclick="setPlayer(2)">ペア</div>
    </div>

    <div id="cur-player" class="active-label">記録中: 自分</div>

    <div class="header">
        <div style="color:#007AFF">得点</div>
        <div style="color:#FF3B30">失点</div>
    </div>

    <div class="grid" id="button-area">
        <!-- JSでボタン生成 -->
    </div>

    <div class="footer">
        <details>
            <summary>⚙️ 設定 / 📊 統計を確認</summary>
            <input type="text" id="in-match" placeholder="試合名" oninput="updateSettings()">
            <input type="text" id="in-p1" placeholder="選手1の名前" oninput="updateSettings()">
            <input type="text" id="in-p2" placeholder="選手2の名前" oninput="updateSettings()">
            <button onclick="resetAll()" style="width:100%; padding:10px; background:#f44336; color:white; border:none; border-radius:4px; margin:10px 0; font-weight:bold;">全リセット</button>
            <div id="stats-area"></div>
        </details>
    </div>

    <script>
        let state = {
            p1_score: 0, p2_score: 0, p1_games: 0, p2_games: 0,
            active: 1, p1_name: "自分", p2_name: "ペア", match: "今日の試合",
            stats: { p1: {}, p2: {} }
        };

        // カウント用全項目
        const wins = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト'];
        const loss = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース'];

        // 統計に表示する項目（ご要望により「相手の〜」を除外）
        const statsToShow = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', 'ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス'];

        function initButtons() {
            const area = document.getElementById('button-area');
            wins.forEach((w, i) => {
                const l = loss[i];
                area.innerHTML += `<div class="btn btn-win" onclick="count('${w}', true)">${w}</div>`;
                area.innerHTML += `<div class="btn btn-loss" onclick="count('${l}', false)">${l}</div>`;
                state.stats.p1[w] = 0; state.stats.p1[l] = 0;
                state.stats.p2[w] = 0; state.stats.p2[l] = 0;
            });
        }

        function setPlayer(n) {
            state.active = n;
            document.getElementById('p1-tag').className = n===1 ? 'p-btn active' : 'p-btn';
            document.getElementById('p2-tag').className = n===2 ? 'p-btn active' : 'p-btn';
            document.getElementById('cur-player').innerText = "記録中: " + (n===1 ? state.p1_name : state.p2_name);
        }

        function count(item, isWin) {
            const p = state.active === 1 ? 'p1' : 'p2';
            state.stats[p][item]++;
            
            if(isWin) state.p1_score++;
            else state.p2_score++;

            if((state.p1_score >= 4 || state.p2_score >= 4) && Math.abs(state.p1_score - state.p2_score) >= 2) {
                if(state.p1_score > state.p2_score) state.p1_games++;
                else state.p2_games++;
                state.p1_score = 0; state.p2_score = 0;
            }
            render();
        }

        function updateSettings() {
            state.match = document.getElementById('in-match').value || "今日の試合";
            state.p1_name = document.getElementById('in-p1').value || "自分";
            state.p2_name = document.getElementById('in-p2').value || "ペア";
            render();
        }

        function render() {
            document.getElementById('points').innerText = state.p1_score + " — " + state.p2_score;
            document.getElementById('games').innerText = "Game: " + state.p1_games + " — " + state.p2_games;
            document.getElementById('match-display').innerText = state.match;
            document.getElementById('names-display').innerText = state.p1_name + " & " + state.p2_name;
            document.getElementById('p1-tag').innerText = state.p1_name;
            document.getElementById('p2-tag').innerText = state.p2_name;
            document.getElementById('cur-player').innerText = "記録中: " + (state.active === 1 ? state.p1_name : state.p2_name);
            
            // 統計テーブル生成
            let h = "<table><tr><th>項目</th><th>" + state.p1_name + "</th><th>" + state.p2_name + "</th></tr>";
            statsToShow.forEach(it => {
                h += `<tr><td>${it}</td><td>${state.stats.p1[it] || 0}</td><td>${state.stats.p2[it] || 0}</td></tr>`;
            });
            document.getElementById('stats-area').innerHTML = h + "</table>";
        }

        function resetAll() {
            if(confirm("全てのデータをリセットしますか？")) { location.reload(); }
        }

        initButtons();
        render();
    </script>
</body>
</html>
"""

# 表示
components.html(html_code, height=850, scrolling=True)
