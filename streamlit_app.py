import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="Tennis Counter Room", layout="centered")

# URLから部屋名を取得（例: xxx.streamlit.app/?room=court1）
# 指定がない場合は "default" という部屋にする
query_params = st.query_params
room_name = query_params.get("room", "default")

st.write(f"現在の部屋: **{room_name}**")
st.caption("URLの末尾に '?room=好きな名前' を付けると別の部屋を作れます")

# HTMLコード（Python変数を一切混ぜない「完全固定」の文字列）
# 前回の「最高！」と言っていただいた多機能版のコードをベースにしています
html_code = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, sans-serif; background: white; padding: 5px; }
        .score-box { background: #222; color: white; border-radius: 10px; text-align: center; padding: 10px; margin-bottom: 8px; }
        .main-score { font-size: 44px; font-weight: 900; line-height: 1; margin: 5px 0; }
        .player-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
        .p-btn { border: 2px solid #E67E22; background: white; color: #E67E22; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; }
        .p-btn.active { background: #E67E22; color: white; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
        .btn { height: 44px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px; border: none; }
        .btn-win { background-color: #007AFF; }
        .btn-loss { background-color: #FF3B30; }
        .undo-btn { background: #666; color: white; border: none; padding: 8px; width: 100%; margin-top: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="score-box">
        <div id="pts" class="main-score">0 — 0</div>
        <div id="gms" style="color:#4CAF50;">Game: 0 — 0</div>
    </div>
    <div class="player-selector">
        <div id="p1" class="p-btn active" onclick="setPlayer(1)">自分</div>
        <div id="p2" class="p-btn" onclick="setPlayer(2)">ペア</div>
    </div>
    <div class="grid" id="btns"></div>
    <button class="undo-btn" onclick="undo()">↩ 一つ戻る</button>

    <script>
        var state = {p1_p:0, p2_p:0, g1:0, g2:0, active:1};
        var history = [];
        var labels = ['エース', 'ミス', 'ボレー', 'ミス', 'スマッシュ', 'ミス', 'サーブ', 'ミス'];

        function setPlayer(n) {
            state.active = n;
            document.getElementById('p1').className = n==1 ? 'p-btn active' : 'p-btn';
            document.getElementById('p2').className = n==2 ? 'p-btn active' : 'p-btn';
        }

        function count(isWin) {
            history.push(JSON.stringify(state));
            if(isWin) state.p1_p++; else state.p2_p++;
            if((state.p1_p>=4||state.p2_p>=4) && Math.abs(state.p1_p-state.p2_p)>=2) {
                if(state.p1_p>state.p2_p) state.g1++; else state.g2++;
                state.p1_p=0; state.p2_p=0;
            }
            render();
        }

        function undo() { if(history.length>0){ state=JSON.parse(history.pop()); render(); } }

        function render() {
            document.getElementById('pts').innerText = state.p1_p + " — " + state.p2_p;
            document.getElementById('gms').innerText = "Game: " + state.g1 + " — " + state.g2;
        }

        var bArea = document.getElementById('btns');
        for(var i=0; i<labels.length; i++) {
            (function(idx){
                var isWin = (idx%2==0);
                var btn = document.createElement('button');
                btn.className = isWin ? 'btn btn-win' : 'btn btn-loss';
                btn.innerText = labels[idx];
                btn.onclick = function(){ count(isWin); };
                bArea.appendChild(btn);
            })(i);
        }
    </script>
</body>
</html>
"""

# 部屋ごとに独立したキーを持たせるが、最もシンプルな形式にする
components.html(html_code, height=600, key="tennis_app_fixed")
