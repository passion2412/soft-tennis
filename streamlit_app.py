import copy
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass

WIN_CATEGORIES = [
    "サービスエース",
    "レシーブエース",
    "スマッシュ",
    "ノータッチエース",
    "ボレー",
    "相手のミス",
]

LOSE_CATEGORIES = [
    "ダブルフォルト",
    "レシーブミス",
    "スマッシュミス",
    "ストロークミス",
    "ボレーミス",
    "相手のエース",
]

TOTAL_GAMES = 5
GAMES_TO_WIN = 3


@dataclass
class GameState:
    our_points: int = 0
    opp_points: int = 0
    finished: bool = False
    winner: str = ""


class SoftTennisScoreApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ソフトテニス スコア記録アプリ")
        self.root.geometry("1300x820")
        self.root.minsize(1180, 760)

        self.history = []
        self.player_stats = {}
        self.games = []
        self.current_game_index = 0
        self.our_games_won = 0
        self.opp_games_won = 0
        self.match_over = False

        self.player_name_vars = [tk.StringVar(value="プレイヤー1"), tk.StringVar(value="プレイヤー2")]
        self.selected_player = tk.IntVar(value=0)
        self.status_var = tk.StringVar(value="準備完了")
        self.match_score_var = tk.StringVar(value="ゲームカウント 0 - 0")
        self.match_result_var = tk.StringVar(value="")

        self.game_labels = []
        self.stat_labels = {}
        self.total_labels = {}

        self._build_ui()
        self.reset_match(initial=True)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=12)
        main.grid(sticky="nsew")
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=4)
        main.rowconfigure(1, weight=1)

        header = ttk.Label(
            main,
            text="ソフトテニス ダブルス 5ゲーム スコア記録",
            font=("Yu Gothic UI", 18, "bold"),
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        left = ttk.LabelFrame(main, text="試合状況", padding=12)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        names_frame = ttk.Frame(left)
        names_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        names_frame.columnconfigure(1, weight=1)
        names_frame.columnconfigure(3, weight=1)

        ttk.Label(names_frame, text="ペア1").grid(row=0, column=0, sticky="w")
        ttk.Entry(names_frame, textvariable=self.player_name_vars[0], width=16).grid(row=0, column=1, sticky="ew", padx=(4, 12))
        ttk.Label(names_frame, text="ペア2").grid(row=0, column=2, sticky="w")
        ttk.Entry(names_frame, textvariable=self.player_name_vars[1], width=16).grid(row=0, column=3, sticky="ew", padx=(4, 0))

        for i, var in enumerate(self.player_name_vars):
            var.trace_add("write", lambda *_: self.refresh_ui())

        score_box = ttk.Frame(left)
        score_box.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        score_box.columnconfigure(0, weight=1)

        ttk.Label(score_box, textvariable=self.match_score_var, font=("Yu Gothic UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(score_box, textvariable=self.match_result_var, foreground="#0b6e4f", font=("Yu Gothic UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(4, 0))

        game_board = ttk.LabelFrame(left, text="各ゲームのポイント", padding=10)
        game_board.grid(row=2, column=0, sticky="nsew")
        game_board.columnconfigure((0, 1), weight=1)

        self.game_labels = []
        for i in range(TOTAL_GAMES):
            frame = ttk.Frame(game_board, relief="ridge", padding=10)
            frame.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            frame.columnconfigure(0, weight=1)
            title = ttk.Label(frame, text=f"第{i + 1}ゲーム", font=("Yu Gothic UI", 12, "bold"))
            title.grid(row=0, column=0, sticky="w")
            point_label = ttk.Label(frame, text="-", font=("Yu Gothic UI", 16, "bold"), foreground="#1d3557")
            point_label.grid(row=1, column=0, sticky="w", pady=(6, 2))
            detail_label = ttk.Label(frame, text="未開始", foreground="#666666")
            detail_label.grid(row=2, column=0, sticky="w")
            self.game_labels.append((point_label, detail_label))

        controls = ttk.Frame(left)
        controls.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(controls, text="1つ戻す", command=self.undo).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(controls, text="試合をリセット", command=self.reset_match).grid(row=0, column=1)

        right = ttk.LabelFrame(main, text="記録入力", padding=12)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        player_select = ttk.LabelFrame(right, text="記録対象プレイヤー", padding=10)
        player_select.grid(row=0, column=0, sticky="ew")
        for i in range(2):
            ttk.Radiobutton(
                player_select,
                textvariable=self.player_name_vars[i],
                value=i,
                variable=self.selected_player,
            ).grid(row=0, column=i, sticky="w", padx=(0, 18))

        info = ttk.Label(
            right,
            text="選択したプレイヤーに対して項目を押すと、個人カウントと試合ポイントが同時に記録されます。",
            foreground="#555555",
            wraplength=620,
        )
        info.grid(row=1, column=0, sticky="w", pady=(10, 12))

        button_area = ttk.Frame(right)
        button_area.grid(row=2, column=0, sticky="nsew")
        button_area.columnconfigure(0, weight=1)
        button_area.columnconfigure(1, weight=1)
        button_area.rowconfigure(0, weight=1)

        win_frame = ttk.LabelFrame(button_area, text="得点項目（自チームに1ポイント）", padding=10)
        win_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        win_frame.columnconfigure(0, weight=1)
        for idx, category in enumerate(WIN_CATEGORIES):
            ttk.Button(
                win_frame,
                text=category,
                command=lambda c=category: self.record_event("win", c),
            ).grid(row=idx, column=0, sticky="ew", pady=4)

        lose_frame = ttk.LabelFrame(button_area, text="失点項目（相手に1ポイント）", padding=10)
        lose_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        lose_frame.columnconfigure(0, weight=1)
        for idx, category in enumerate(LOSE_CATEGORIES):
            ttk.Button(
                lose_frame,
                text=category,
                command=lambda c=category: self.record_event("lose", c),
            ).grid(row=idx, column=0, sticky="ew", pady=4)

        stats_frame = ttk.LabelFrame(right, text="個人別カウント", padding=10)
        stats_frame.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        self.stat_labels = {0: {}, 1: {}}
        self.total_labels = {}

        all_categories = [("得点", WIN_CATEGORIES), ("失点", LOSE_CATEGORIES)]

        for col in range(2):
            frame = ttk.LabelFrame(stats_frame, textvariable=self.player_name_vars[col], padding=10)
            frame.grid(row=0, column=col, sticky="nsew", padx=6)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            row = 0
            for section_name, categories in all_categories:
                ttk.Label(frame, text=section_name, font=("Yu Gothic UI", 11, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
                row += 1
                for category in categories:
                    ttk.Label(frame, text=category).grid(row=row, column=0, sticky="w", pady=1)
                    value = ttk.Label(frame, text="0", width=6, anchor="e")
                    value.grid(row=row, column=1, sticky="e", pady=1)
                    self.stat_labels[col][category] = value
                    row += 1
                row += 1
            ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)
            row += 1
            ttk.Label(frame, text="合計", font=("Yu Gothic UI", 11, "bold")).grid(row=row, column=0, sticky="w")
            total_value = ttk.Label(frame, text="0", width=6, anchor="e", font=("Yu Gothic UI", 11, "bold"))
            total_value.grid(row=row, column=1, sticky="e")
            self.total_labels[col] = total_value

        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(8, 4))
        status_bar.grid(row=1, column=0, sticky="ew")

    def empty_stats(self):
        return {
            "win": {category: 0 for category in WIN_CATEGORIES},
            "lose": {category: 0 for category in LOSE_CATEGORIES},
        }

    def capture_state(self):
        return {
            "player_stats": copy.deepcopy(self.player_stats),
            "games": copy.deepcopy(self.games),
            "current_game_index": self.current_game_index,
            "our_games_won": self.our_games_won,
            "opp_games_won": self.opp_games_won,
            "match_over": self.match_over,
            "status": self.status_var.get(),
            "match_result": self.match_result_var.get(),
        }

    def restore_state(self, state):
        self.player_stats = copy.deepcopy(state["player_stats"])
        self.games = copy.deepcopy(state["games"])
        self.current_game_index = state["current_game_index"]
        self.our_games_won = state["our_games_won"]
        self.opp_games_won = state["opp_games_won"]
        self.match_over = state["match_over"]
        self.status_var.set(state["status"])
        self.match_result_var.set(state["match_result"])
        self.refresh_ui()

    def reset_match(self, initial=False):
        if not initial:
            ok = messagebox.askyesno("確認", "現在の記録をリセットしますか？")
            if not ok:
                return
        self.history = []
        self.player_stats = {0: self.empty_stats(), 1: self.empty_stats()}
        self.games = [GameState() for _ in range(TOTAL_GAMES)]
        self.current_game_index = 0
        self.our_games_won = 0
        self.opp_games_won = 0
        self.match_over = False
        self.match_result_var.set("")
        self.status_var.set("新しい試合を開始しました")
        self.refresh_ui()

    def point_text(self, our_points, opp_points):
        return f"{our_points} - {opp_points}"

    def record_event(self, event_type, category):
        if self.match_over:
            messagebox.showinfo("試合終了", "この試合は終了しています。リセットしてから記録してください。")
            return
        if self.current_game_index >= TOTAL_GAMES:
            return

        self.history.append(self.capture_state())

        player = self.selected_player.get()
        self.player_stats[player][event_type][category] += 1

        game = self.games[self.current_game_index]
        if event_type == "win":
            game.our_points += 1
            side_text = "自チーム得点"
        else:
            game.opp_points += 1
            side_text = "相手得点"

        player_name = self.player_name_vars[player].get().strip() or f"プレイヤー{player + 1}"
        self.status_var.set(f"{player_name}: {category} を記録（{side_text}）")

        self._check_game_end()
        self.refresh_ui()

    def _check_game_end(self):
        game = self.games[self.current_game_index]
        if game.finished:
            return

        if max(game.our_points, game.opp_points) >= 4 and abs(game.our_points - game.opp_points) >= 2:
            game.finished = True
            if game.our_points > game.opp_points:
                game.winner = "自チーム"
                self.our_games_won += 1
                self.status_var.set(f"第{self.current_game_index + 1}ゲーム終了：自チームが取得")
            else:
                game.winner = "相手"
                self.opp_games_won += 1
                self.status_var.set(f"第{self.current_game_index + 1}ゲーム終了：相手が取得")

            if self.our_games_won >= GAMES_TO_WIN or self.opp_games_won >= GAMES_TO_WIN or self.current_game_index == TOTAL_GAMES - 1:
                self.match_over = True
                if self.our_games_won > self.opp_games_won:
                    self.match_result_var.set("試合結果: 自チームの勝ち")
                elif self.opp_games_won > self.our_games_won:
                    self.match_result_var.set("試合結果: 相手の勝ち")
                else:
                    self.match_result_var.set("試合結果: 引き分け")
            else:
                self.current_game_index += 1

    def undo(self):
        if not self.history:
            messagebox.showinfo("戻す", "戻せる記録がありません。")
            return
        previous = self.history.pop()
        self.restore_state(previous)
        self.status_var.set("1つ前の記録に戻しました")

    def refresh_ui(self):
        self.match_score_var.set(f"ゲームカウント {self.our_games_won} - {self.opp_games_won}")

        for i, game in enumerate(self.games):
            point_label, detail_label = self.game_labels[i]
            if i < self.current_game_index or game.finished:
                point_label.config(text=self.point_text(game.our_points, game.opp_points))
                detail_label.config(text=f"終了 / 勝者: {game.winner}")
            elif i == self.current_game_index and not self.match_over:
                point_label.config(text=self.point_text(game.our_points, game.opp_points))
                detail_label.config(text="進行中")
            else:
                point_label.config(text="-")
                detail_label.config(text="未開始")

        if self.match_over and self.current_game_index < TOTAL_GAMES:
            game = self.games[self.current_game_index]
            if not game.finished and (game.our_points > 0 or game.opp_points > 0):
                self.game_labels[self.current_game_index][0].config(text=self.point_text(game.our_points, game.opp_points))
                self.game_labels[self.current_game_index][1].config(text="終了")

        for player in range(2):
            total = 0
            for category in WIN_CATEGORIES:
                value = self.player_stats[player]["win"][category]
                self.stat_labels[player][category].config(text=str(value))
                total += value
            for category in LOSE_CATEGORIES:
                value = self.player_stats[player]["lose"][category]
                self.stat_labels[player][category].config(text=str(value))
                total += value
            self.total_labels[player].config(text=str(total))


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    app = SoftTennisScoreApp(root)
    root.mainloop()
