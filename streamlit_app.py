import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="Tennis Counter Room Full", layout="centered")

# HTML本体（設定・詳細レポート・履歴をすべてJS側で完結させた最強版）
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, sans-serif; background: white; padding: 5px; }
        .room-tag { font-size: 10px; color: #999; text-align: center; }
        .match-name { text-align: center; font-size: 16px; font-weight: bold; color: #333; margin: 5px 0; }
        .score-box { background: #222; color: white; border-radius: 10px; text-align: center; padding: 10px; margin-bottom: 8px; }
        .main-score { font-size: 48px; font-weight: 900; line-height: 1; margin: 5px 0; }
        .game-score { font-size: 18px; color: #4CAF50; font-weight: bold; }
        .player-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
        .p-btn { border: 2px solid #E67E22; background: white; color: #E67E22; padding: 10px; border-radius: 6px; font-weight: bold; text-align: center; }
        .p-btn.active { background: #E67E22; color: white; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
        .btn { height: 46px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white !important; font-weight: bold; font-size: 11px; border: none; }
        .btn-win { background-color: #007AFF; }
        .btn-loss { background-color: #FF3B30; }
        .undo-btn { background: #666; color: white; border: none; padding: 10px; width: 100%; margin-top: 10px; border-radius: 4px; font-weight: bold; }
        
        .report-card { border: 2px solid #333; border-radius: 8px; padding: 10px; margin-top: 20px; background: #fff; }
        .report-title { font-size: 14px; font-weight: bold; background: #333; color: white; margin: -10px -10px 10px -10px; padding: 8px; border-radius: 6px 6px 0 0; text-align: center; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 6px; text-align: center; }
        th { background: #f4f4f4; }
        .history-grid { display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; margin-top: 10px; }
        .history-item { border: 1px solid #333; border-radius: 4px; padding: 3px 8px; font-size: 12px; font-weight: bold; background: #eee; }
        
        details { margin-top: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="room-tag">ROOM: <input type="text" id="room-id" value="Room1" style="width:60px; padding:2px; font-size:10px; display:inline;"> (自分とお友達で違う名前にしてね)</div>
    
    <div id="disp-match" class="match-name">今日の試合</div>
    <div class="score-box">
        <div id="disp-names" style="font-size: 12px; opacity: 0.9;">自分 & ペア vs 相手</div>
        <div id="pts" class="main-score">0 — 0</div>
        <div id="gms" class="game-score">Game: 0 — 0</div>
    </div>

    <div class="player-selector">
        <div id="tag1" class="p-btn active" onclick="setPlayer(1)">自分</div>
        <div id="tag2" class="p-btn" onclick="setPlayer(2)">ペア</div>
    </div>

    <div class="grid" id="btns"></div>
    <button class="undo-btn" onclick="undo()">↩ 一つ戻る</button>

    <div class="report-card">
        <div class="report-title">FINAL MATCH REPORT</div>
        <div style="text-align:center; font-weight:bold; margin-bottom:10px;">
            <span id="final-gms" style="font-size:26px; color:#d32f2f;">0 — 0</span><br>
            <span id="final-names" style="font-size:13px;">自分 & ペア vs 相手</span>
        </div>
        <table>
            <thead><tr id="stats-head"><th>項目</th><th>自分</th><th>ペア</th></tr></thead>
            <tbody id="stats-body"></tbody>
        </table>
        <div style="font-size:11px; font-weight:bold; color:#d32f2f; margin:10px 0 5px 0;">相手によるポイント</div>
        <table>
            <tr><th style="width:50%">項目</th><th>回数</th></tr>
            <tr><td>相手のエース</td><td id="opp-ace">0</td></tr>
            <tr><td>相手のミス</td><td id="opp-miss">0</td></tr>
        </table>
        <div style="font-size:11px; font-weight:bold; color:#666; margin-top:15px; text-align:center;">GAME HISTORY</div>
        <div id="history-area" class="history-grid"></div>
    </div>

    <details>
        <summary>⚙️ 名前・試合設定</summary>
        <input type="text" id="in-match" placeholder="試合名 (例: 1回戦)" oninput="updateSettings()">
        <input type="text" id="in-p1" placeholder="自分の名前" oninput="updateSettings()">
        <input type="text" id="in-p2" placeholder="ペアの名前" oninput="updateSettings()">
        <input type="text" id="in-opp" placeholder="対戦相手の名前" oninput="updateSettings()">
        <button onclick="location.reload()" style="background:#f44336; color:white; width:100%; padding:10px; border:none; border-radius:4px; margin-top:10px;">全データをリセット</button>
    </details>

    <script>
        var state = {
            p1:0, p2:0, g1:0, g2:0, active:1,
            match: "今日の試合", p1_n: "自分", p2_n: "ペア", opp_n: "相手",
            stats: { p1: {}, p2: {} },
            opp_ace: 0, opp_miss: 0, history: []
        };
        var stack = [];
        var wins = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス'];
        var loss = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース'];
        var stats_list = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', 'ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス'];

        function init() {
            var bArea = document.getElementById('btns');
            wins.forEach(function(w, i) {
                var l = loss[i];
                bArea.innerHTML += '<button class="btn btn-win" onclick="count(\''+w+'\', true)">'+w+'</button>';
                bArea.innerHTML += '<button class="btn btn-loss" onclick="count(\''+l+'\', false)">'+l+'</button>';
                state.stats.p1[w] = 0; state.stats.p1[l] = 0;
                state.stats.p2[w] = 0; state.stats.p2[l] = 0;
            });
            render();
        }

        function setPlayer(n) { state.active = n; render(); }

        function count(label, isWin) {
            stack.push(JSON.stringify(state));
            if(label === '相手のエース') state.opp_ace++;
            if(label === '相手のミス') state.opp_miss++;
            var pKey = state.active == 1 ? 'p1' : 'p2';
            state.stats[pKey][label]++;

            if(isWin) state.p1++; else state.p2++;
            if((state.p1 >= 4 || state.p2 >= 4) && Math.abs(state.p1 - state.p2) >= 2) {
                state.history.push(state.p1 + "-" + state.p2);
                if(state.p1 > state.p2) state.g1++; else state.g2++;
                state.p1 = 0; state.p2 = 0;
            }
            render();
        }

        function undo() { if(stack.length > 0) { state = JSON.parse(stack.pop()); render(); } }

        function updateSettings() {
            state.match = document.getElementById('in-match').value || "今日の試合";
            state.p1_n = document.getElementById('in-p1').value || "自分";
            state.p2_n = document.getElementById('in-p2').value || "ペア";
            state.opp_n = document.getElementById('in-opp').value || "相手";
            render();
        }

        function render() {
            document.getElementById('pts').innerText = state.p1 + " — " + state.p2;
            document.getElementById('gms').innerText = "Game: " + state.g1 + " — " + state.g2;
            document.getElementById('disp-match').innerText = state.match;
            document.getElementById('disp-names').innerText = state.p1_n + " & " + state.p2_n + " vs " + state.opp_n;
            document.getElementById('tag1').innerText = state.p1_n;
            document.getElementById('tag2').innerText = state.p2_n;
            document.getElementById('tag1').className = state.active==1 ? 'p-btn active' : 'p-btn';
            document.getElementById('tag2').className = state.active==2 ? 'p-btn active' : 'p-btn';
            
            // レポート更新
            document.getElementById('final-gms').innerText = state.g1 + " — " + state.g2;
            document.getElementById('final-names').innerText = state.p1_n + " & " + state.p2_n + " vs " + state.opp_n;
            document.getElementById('stats-head').innerHTML = "<th>項目</th><th>"+state.p1_n+"</th><th>"+state.p2_n+"</th>";
            var rows = "";
            stats_list.forEach(function(s){
                rows += "<tr><td style='text-align:left;'>"+s+"</td><td>"+(state.stats.p1[s]||0)+"</td><td>"+(state.stats.p2[s]||0)+"</td></tr>";
            });
            document.getElementById('stats-body').innerHTML = rows;
            document.getElementById('opp-ace').innerText = state.opp_ace;
            document.getElementById('opp-miss').innerText = state.opp_miss;
            
            var histHTML = "";
            state.history.forEach(function(h, i){ histHTML += '<div class="history-item">G'+(i+1)+': '+h+'</div>'; });
            document.getElementById('history-area').innerHTML = histHTML || "...";
        }
        init();
    </script>
</body>
</html>
"""

# 表示
components.html(html_code, height=1300, scrolling=True)
