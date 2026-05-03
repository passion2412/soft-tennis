import streamlit as st
import streamlit.components.v1 as components

# 1. ページ設定（これだけはPythonで書く必要があります）
st.set_page_config(page_title="Tennis Counter Room", layout="centered")

# 2. HTML本体
# Pythonの変数（f-stringなど）を一切使わない「完全な固定文字列」にします
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, sans-serif; background: white; padding: 5px; }
        .match-name { text-align: center; font-size: 14px; font-weight: bold; color: #666; margin-bottom: 5px; }
        .score-box { background: #222; color: white; border-radius: 10px; text-align: center; padding: 10px; margin-bottom: 8px; }
        .main-score { font-size: 44px; font-weight: 900; line-height: 1; margin: 5px 0; }
        .game-score { font-size: 16px; color: #4CAF50; font-weight: bold; }
        .undo-btn { background: #666; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 12px; }
        .player-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
        .p-btn { border: 2px solid #E67E22; background: white; color: #E67E22; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; }
        .p-btn.active { background: #E67E22; color: white; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
        .btn { height: 44px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white !important; font-weight: bold; font-size: 11px; border: none; }
        .btn-win { background-color: #007AFF; }
        .btn-loss { background-color: #FF3B30; }
        .report-card { border: 2px solid #333; border-radius: 8px; padding: 10px; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 11px; }
        th, td { border: 1px solid #ddd; padding: 5px; text-align: center; }
    </style>
</head>
<body>
    <!-- 部屋番号の入力欄をHTML側に作成（Pythonのエラーを回避） -->
    <div style="background:#f0f0f0; padding:10px; border-radius:5px; margin-bottom:10px;">
        <label style="font-size:12px; font-weight:bold;">🔑 部屋番号（合言葉）:</label>
        <input type="text" id="room-input" value="Room1" oninput="changeRoom()" style="width:100px;">
        <span style="font-size:10px; color:#666;">※違う名前にするとデータが混ざりません</span>
    </div>

    <div id="match-display" class="match-name">今日の試合</div>
    <div class="score-box">
        <div id="points" class="main-score">0 — 0</div>
        <div id="games" class="game-score">Game: 0 — 0</div>
    </div>
    <div class="player-selector">
        <div id="p1-tag" class="p-btn active" onclick="setPlayer(1)">自分</div>
        <div id="p2-tag" class="p-btn" onclick="setPlayer(2)">ペア</div>
    </div>
    <div class="grid" id="button-area"></div>
    <button class="undo-btn" style="width:100%; margin-top:10px;" onclick="undo()">↩ 一つ戻る</button>

    <div class="report-card">
        <div style="text-align:center; font-weight:bold;">FINAL REPORT</div>
        <table id="stats-table" style="margin-top:10px;">
            <thead><tr><th>ショット</th><th>自分</th><th>ペア</th></tr></thead>
            <tbody id="stats-body"></tbody>
        </table>
    </div>

    <script>
        // 部屋ごとにデータを分けるための仕組み
        var currentRoom = "Room1";
        var state = { p1_score: 0, p2_score: 0, p1_games: 0, p2_games: 0, active: 1, stats: { p1: {}, p2: {} } };
        var stack = [];
        var labels = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス', 'ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース'];

        function changeRoom() {
            currentRoom = document.getElementById('room-input').value;
            // 実際にはブラウザ内のメモリで動くので、入力を変えるだけでリセットに近い状態になります
        }

        function setPlayer(n) {
            state.active = n;
            document.getElementById('p1-tag').className = n==1 ? 'p-btn active' : 'p-btn';
            document.getElementById('p2-tag').className = n==2 ? 'p-btn active' : 'p-btn';
        }

        function count(label, isWin) {
            stack.push(JSON.stringify(state));
            var pKey = state.active == 1 ? 'p1' : 'p2';
            state.stats[pKey][label] = (state.stats[pKey][label] || 0) + 1;
            
            if(isWin) state.p1_score++; else state.p2_score++;
            if((state.p1_score >= 4 || state.p2_score >= 4) && Math.abs(state.p1_score - state.p2_score) >= 2) {
                if(state.p1_score > state.p2_score) state.p1_games++; else state.p2_games++;
                state.p1_score = 0; state.p2_score = 0;
            }
            render();
        }

        function undo() { if(stack.length > 0) { state = JSON.parse(stack.pop()); render(); } }

        function render() {
            document.getElementById('points').innerText = state.p1_score + " — " + state.p2_score;
            document.getElementById('games').innerText = "Game: " + state.p1_games + " — " + state.p2_games;
            var rows = "";
            labels.slice(0, 6).forEach(function(l){
                rows += "<tr><td>"+l+"</td><td>"+(state.stats.p1[l]||0)+"</td><td>"+(state.stats.p2[l]||0)+"</td></tr>";
            });
            document.getElementById('stats-body').innerHTML = rows;
        }

        var area = document.getElementById('button-area');
        labels.forEach(function(l, i){
            var isWin = i < 6;
            var btn = document.createElement('div');
            btn.className = isWin ? 'btn btn-win' : 'btn btn-loss';
            btn.innerText = l;
            btn.onclick = function(){ count(l, isWin); };
            area.appendChild(btn);
        });
        render();
    </script>
</body>
</html>
"""

# Python側の不安定な引数（keyなど）をすべて削除して表示
components.html(html_code, height=1000, scrolling=True)
