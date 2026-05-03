import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="Tennis Stats for Screenshot", layout="centered")

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
        .score-box { background: #222; color: white; border-radius: 10px; text-align: center; padding: 10px; margin-bottom: 10px; }
        .main-score { font-size: 40px; font-weight: 900; line-height: 1; margin: 5px 0; }
        .game-score { font-size: 14px; color: #4CAF50; font-weight: bold; }

        /* ボタン */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 10px; }
        .btn { 
            height: 42px; border-radius: 5px; display: flex; align-items: center; justify-content: center; 
            color: white !important; font-weight: bold; font-size: 11px; text-align: center; border: none;
        }
        .btn-win { background-color: #007AFF; }
        .btn-loss { background-color: #FF3B30; }

        /* 統計・履歴エリア (スクショ用) */
        .ss-container { border: 1px solid #ddd; border-radius: 8px; padding: 8px; background: #fdfdfd; margin-top: 10px; }
        .ss-title { font-size: 12px; font-weight: bold; border-bottom: 1px solid #eee; margin-bottom: 5px; padding-bottom: 2px; text-align: center; }
        
        table { width: 100%; border-collapse: collapse; font-size: 10px; margin-bottom: 10px; }
        th, td { border: 1px solid #eee; padding: 4px; text-align: center; }
        th { background: #f8f9fa; }

        /* ゲーム履歴用スタイル */
        .history-box { display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; font-size: 11px; font-weight: bold; }
        .history-item { background: #eee; padding: 2px 6px; border-radius: 4px; border: 1px solid #ccc; }

        .footer { margin-top: 15px; }
        input { width: 100%; padding: 6px; margin: 3px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 12px; }
    </style>
</head>
<body>

    <div id="match-display" class="match-name">今日の試合</div>

    <div class="score-box">
        <div id="names-display" style="font-size: 11px; opacity: 0.8;">自分 & ペア vs 相手</div>
        <div id="points" class="main-score">0 — 0</div>
        <div id="games" class="game-score">Game: 0 — 0</div>
    </div>

    <div class="grid" id="button-area"></div>

    <!-- スクショ保存用エリア -->
    <div class="ss-container">
        <div class="ss-title">📊 試合レポート</div>
        <div id="stats-area"></div>
        
        <div class="ss-title">🎾 ゲーム履歴 (各ゲームの得点)</div>
        <div id="history-area" class="history-box"></div>
    </div>

    <div class="footer">
        <details>
            <summary style="font-size:12px;">⚙️ 設定・名前入力</summary>
            <input type="text" id="in-match" placeholder="試合名" oninput="updateSettings()">
            <input type="text" id="in-p1" placeholder="自分" oninput="updateSettings()">
            <input type="text" id="in-p2" placeholder="ペア" oninput="updateSettings()">
            <input type="text" id="in-opp" placeholder="対戦相手名" oninput="updateSettings()">
            <button onclick="location.reload()" style="width:100%; padding:8px; background:#f44336; color:white; border:none; border-radius:4px; margin-top:10px; font-size:11px;">全リセット</button>
        </details>
    </div>

    <script>
        let state = {
            p1_score: 0, p2_score: 0, p1_games: 0, p2_games: 0,
            p1_name: "自分", p2_name: "ペア", opp_name: "対戦相手", match: "今日の試合",
            stats: { p1: {}, p2: {} },
            game_history: [] // ゲームごとのスコアを保存
        };

        const wins = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', '相手のダブルフォルト'];
        const loss = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース', '相手のサービスエース'];
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

        function count(item, isWin) {
            // 現在は簡易的に「自分」の統計として加算（必要なら選手選択機能も復活可）
            state.stats.p1[item]++;
            
            if(isWin) state.p1_score++;
            else state.p2_score++;

            if((state.p1_score >= 4 || state.p2_score >= 4) && Math.abs(state.p1_score - state.p2_score) >= 2) {
                // ゲーム終了。履歴に追加
                state.game_history.push(state.p1_score + "-" + state.p2_score);
                
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
            state.opp_name = document.getElementById('in-opp').value || "対戦相手";
            render();
        }

        function render() {
            document.getElementById('points').innerText = state.p1_score + " — " + state.p2_score;
            document.getElementById('games').innerText = "Total Games: " + state.p1_games + " — " + state.p2_games;
            document.getElementById('match-display').innerText = state.match;
            document.getElementById('names-display').innerText = state.p1_name + " & " + state.p2_name + " vs " + state.opp_name;
            
            // 統計テーブル
            let h = "<table><tr><th>項目</th><th>合計</th></tr>";
            statsToShow.forEach(it => {
                let total = (state.stats.p1[it] || 0) + (state.stats.p2[it] || 0);
                h += `<tr><td>${it}</td><td>${total}</td></tr>`;
            });
            document.getElementById('stats-area').innerHTML = h + "</table>";

            // 履歴表示
            let histH = "";
            state.game_history.forEach((g, i) => {
                histH += `<span class="history-item">G${i+1}: ${g}</span>`;
            });
            document.getElementById('history-area').innerHTML = histH || "進行中...";
        }

        initButtons();
        render();
    </script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
