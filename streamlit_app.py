import streamlit as st
import streamlit.components.v1 as components

# 1. ページ設定
st.set_page_config(page_title="Tennis Counter Rooms", layout="centered")

# 2. 部屋番号の入力（URLを共有しても、ここで入力した名前が違うとデータが混ざりません）
room_id = st.text_input("🔑 部屋番号（合言葉）を入力してください", "RoomA", help="友人と別々に使うときは、ここを違う名前にしてください")

if room_id:
    # 部屋ごとに独立したHTMLを表示（keyにroom_idを含めることでキャッシュ混同を防ぐ）
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: -apple-system, sans-serif; background-color: white; color: black; margin: 0; padding: 5px; }}
            .room-banner {{ text-align: center; font-size: 10px; color: #aaa; margin-bottom: 2px; }}
            .match-name {{ text-align: center; font-size: 14px; margin-bottom: 5px; color: #666; font-weight: bold; }}
            .score-box {{ background: #222; color: white; border-radius: 10px; text-align: center; padding: 10px; margin-bottom: 8px; }}
            .main-score {{ font-size: 44px; font-weight: 900; line-height: 1; margin: 5px 0; }}
            .game-score {{ font-size: 16px; color: #4CAF50; font-weight: bold; }}
            .toolbar {{ display: flex; justify-content: flex-end; margin-bottom: 8px; }}
            .undo-btn {{ background: #666; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .player-selector {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }}
            .p-btn {{ border: 2px solid #E67E22; background: white; color: #E67E22; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; font-size: 13px; }}
            .p-btn.active {{ background: #E67E22; color: white; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 10px; }}
            .btn {{ height: 44px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white !important; font-weight: bold; font-size: 11px; text-align: center; border: none; }}
            .btn-win {{ background-color: #007AFF; }}
            .btn-loss {{ background-color: #FF3B30; }}
            .report-card {{ border: 2px solid #333; border-radius: 8px; padding: 10px; background: #fff; margin-top: 15px; }}
            .report-title {{ font-size: 13px; font-weight: bold; background: #333; color: white; margin: -10px -10px 10px -10px; padding: 5px; border-radius: 6px 6px 0 0; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 5px; text-align: center; }}
            th {{ background: #f4f4f4; }}
            .history-section {{ border-top: 1px dashed #ccc; padding-top: 10px; text-align: center; }}
            .history-grid {{ display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }}
            .history-item {{ border: 1px solid #333; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold; background: #eee; }}
            .footer {{ margin-top: 20px; padding-bottom: 50px; }}
        </style>
    </head>
    <body>
        <div class="room-banner">ROOM ID: {room_id}</div>
        <div id="match-display" class="match-name">今日の試合</div>
        <div class="score-box">
            <div id="names-display" style="font-size: 11px; opacity: 0.9;">自分 & ペア vs 相手</div>
            <div id="points" class="main-score">0 — 0</div>
            <div id="games" class="game-score">Game: 0 — 0</div>
        </div>
        <div class="toolbar"><button class="undo-btn" onclick="undo()">↩ 一つ戻る</button></div>
        <div class="player-selector">
            <div id="p1-tag" class="p-btn active" onclick="setPlayer(1)">自分</div>
            <div id="p2-tag" class="p-btn" onclick="setPlayer(2)">ペア</div>
        </div>
        <div class="grid" id="button-area"></div>
        <div class="report-card">
            <div class="report-title">FINAL MATCH REPORT</div>
            <div style="text-align:center; font-weight:bold; margin-bottom:10px;">
                <span id="final-games" style="font-size:22px; color:#d32f2f;">0 — 0</span><br>
                <span id="final-names" style="font-size:12px;">自分 & ペア vs 相手</span>
            </div>
            <table><thead id="stats-head"></thead><tbody id="stats-body"></tbody></table>
            <div style="font-size:10px; font-weight:bold; color:#d32f2f; margin-bottom:3px;">相手によるポイント</div>
            <table><tr><th style="width:50%">項目</th><th>回数</th></tr><tr><td>相手のエース</td><td id="opp-ace-count">0</td></tr><tr><td>相手のミス</td><td id="opp-miss-count">0</td></tr></table>
            <div class="history-section">
                <div style="font-size:10px; font-weight:bold; color:#666; margin-bottom:5px;">GAME HISTORY</div>
                <div id="history-area" class="history-grid"></div>
            </div>
        </div>
        <div class="footer">
            <details>
                <summary style="font-size:12px;">⚙️ 設定</summary>
                <input type="text" id="in-match" placeholder="試合名" oninput="updateSettings()" style="width:100%; padding:8px; margin:4px 0;">
                <input type="text" id="in-p1" placeholder="自分の名前" oninput="updateSettings()" style="width:100%; padding:8px; margin:4px 0;">
                <input type="text" id="in-p2" placeholder="ペアの名前" oninput="updateSettings()" style="width:100%; padding:8px; margin:4px 0;">
                <input type="text" id="in-opp" placeholder="対戦相手名" oninput="updateSettings()" style="width:100%; padding:8px; margin:4px 0;">
                <button onclick="location.reload()" style="width:100%; padding:10px; background:#f44336; color:white; border:none; border-radius:4px; margin-top:10px;">リセット</button>
            </details>
        </div>
        <script>
            let state = {{ p1_score: 0, p2_score: 0, p1_games: 0, p2_games: 0, active: 1, p1_name: "自分", p2_name: "ペア", opp_name: "相手", match: "今日の試合", stats: {{ p1: {{}}, p2: {{}} }}, opp_ace: 0, opp_miss: 0, history: [] }};
            let stack = [];
            const wins = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', '相手のミス'];
            const loss = ['ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス', '相手のエース'];
            const pairStats = ['サービスエース', 'レシーブエース', 'スマッシュ', 'エース', 'ボレー', 'ダブルフォルト', 'レシーブミス', 'スマッシュミス', 'ストロークミス', 'ボレーミス'];

            function init() {{
                const area = document.getElementById('button-area');
                wins.forEach((w, i) => {{
                    const l = loss[i];
                    area.innerHTML += `<div class="btn btn-win" onclick="count('${{w}}', true)">${{w}}</div>`;
                    area.innerHTML += `<div class="btn btn-loss" onclick="count('${{l}}', false)">${{l}}</div>`;
                    state.stats.p1[w] = 0; state.stats.p1[l] = 0;
                    state.stats.p2[w] = 0; state.stats.p2[l] = 0;
                }});
                render();
            }}
            function saveStack() {{ stack.push(JSON.stringify(state)); if (stack.length > 50) stack.shift(); }}
            function undo() {{ if (stack.length > 0) {{ state = JSON.parse(stack.pop()); render(); }} }}
            function setPlayer(n) {{ state.active = n; render(); }}
            function count(item, isWin) {{
                saveStack();
                if (item === '相手のエース') state.opp_ace++;
                if (item === '相手のミス') state.opp_miss++;
                const pKey = state.active === 1 ? 'p1' : 'p2';
                state.stats[pKey][item]++;
                if(isWin) state.p1_score++; else state.p2_score++;
                if((state.p1_score >= 4 || state.p2_score >= 4) && Math.abs(state.p1_score - state.p2_score) >= 2) {{
                    state.history.push(state.p1_score + "-" + state.p2_score);
                    if(state.p1_score > state.p2_score) state.p1_games++; else state.p2_games++;
                    state.p1_score = 0; state.p2_score = 0;
                }}
                render();
            }}
            function updateSettings() {{
                state.match = document.getElementById('in-match').value || "今日の試合";
                state.p1_name = document.getElementById('in-p1').value || "自分";
                state.p2_name = document.getElementById('in-p2').value || "ペア";
                state.opp_name = document.getElementById('in-opp').value || "相手";
                render();
            }}
            function render() {{
                document.getElementById('points').innerText = state.p1_score + " — " + state.p2_score;
                document.getElementById('games').innerText = "Game: " + state.p1_games + " — " + state.p2_games;
                document.getElementById('match-display').innerText = state.match;
                document.getElementById('names-display').innerText = state.p1_name + " & " + state.p2_name + " vs " + state.opp_name;
                document.getElementById('final-games').innerText = state.p1_games + " — " + state.p2_games;
                document.getElementById('final-names').innerText = state.p1_name + " & " + state.p2_name + " vs " + state.opp_name;
                document.getElementById('p1-tag').innerText = state.p1_name;
                document.getElementById('p2-tag').innerText = state.p2_name;
                document.getElementById('p1-tag').className = state.active===1 ? 'p-btn active' : 'p-btn';
                document.getElementById('p2-tag').className = state.active===2 ? 'p-btn active' : 'p-btn';
                document.getElementById('stats-head').innerHTML = `<tr><th>ショット</th><th>${{state.p1_name}}</th><th>${{state.p2_name}}</th></tr>`;
                let rows = "";
                pairStats.forEach(s => {{ rows += `<tr><td style="text-align:left; font-weight:bold;">${{s}}</td><td>${{state.stats.p1[s] || 0}}</td><td>${{state.stats.p2[s] || 0}}</td></tr>`; }});
                document.getElementById('stats-body').innerHTML = rows;
                document.getElementById('opp-ace-count').innerText = state.opp_ace;
                document.getElementById('opp-miss-count').innerText = state.opp_miss;
                let hH = ""; state.history.forEach((score, i) => {{ hH += `<div class="history-item">G${{i+1}}: ${{score}}</div>`; }});
                document.getElementById('history-area').innerHTML = hH || "...";
            }}
            init();
        </script>
    </body>
    </html>
    """
    # 部屋ごとに独立したインスタンスとして扱う
    components.html(html_code, height=1300, scrolling=True, key=f"room_{room_id}")
