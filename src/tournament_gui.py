import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Player import Player
from main import pair_round, calculate_standings
import copy

class TournamentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tournament Manager")
        self.players = []
        self.dropped_players = []
        self.current_pairs = []
        self.round_number = 1
        self.num_rounds = 0
        self.round_history = []
        self.result_data = {}
        self.saved_results_history = []

        self.setup_styles()
        self.create_menu_bar()
        self.setup_player_entry_screen()

    def setup_styles(self):
        style = ttk.Style()
        self.root.configure(bg="#2e2e2e")
        style.theme_use("clam")

        font = ("Segoe UI", 11)
        heading_font = ("Segoe UI", 14, "bold")
        bg = "#2e2e2e"
        fg = "#ffffff"
        accent = "#444444"

        style.configure(".", font=font)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=accent, foreground=fg, padding=6)
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TRadiobutton", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg, font=heading_font)

        style.map("TButton", background=[], foreground=[])
        style.map("TCheckbutton", background=[], foreground=[])
        style.map("TRadiobutton", background=[], foreground=[])

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tournament_menu = tk.Menu(menubar, tearoff=0)
        tournament_menu.add_command(label="Submit Round Results", command=self.submit_results)
        tournament_menu.add_command(label="View Standings", command=self.view_standings)
        tournament_menu.add_command(label="Undo Last Round", command=self.undo_last_round)
        tournament_menu.add_command(label="Add Late Player", command=self.add_late_player)
        menubar.add_cascade(label="Tournament", menu=tournament_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Tournament Software Created by James Cunningam/Princeblueblood. \nBuilt with ❤️ using Tkinter."))
        help_menu.add_command(label="Usage", command=lambda: messagebox.showinfo("Info:", "You can add players, remove players, Submit match results, view standings, and redo last round."))
        menubar.add_cascade(label="Help", menu=help_menu)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()

    def setup_player_entry_screen(self):
        self.clear_screen()
        frame = ttk.Frame(self.root)
        frame.pack(padx=40, pady=30)

        ttk.Label(frame, text="Enter Player Names", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        self.player_entry = ttk.Entry(frame, width=30)
        self.player_entry.grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(frame, text="Add Player", command=self.add_player).grid(row=1, column=1, padx=5)

        self.player_listbox = tk.Listbox(frame, bg="#1e1e1e", fg="white", width=40, height=20, font=("Segoe UI", 10), selectbackground="#444", selectforeground="white", relief="flat", bd=2)
        self.player_listbox.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

        ttk.Button(frame, text="Remove Selected", command=self.remove_selected_player).grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="Start Tournament", command=self.start_tournament).grid(row=3, column=1, pady=10)

    def add_player(self):
        name = self.player_entry.get().strip()
        if name and all(p.name != name for p in self.players):
            self.players.append(Player(name))
            self.player_listbox.insert(tk.END, name)
            self.player_entry.delete(0, tk.END)
            self.player_entry.focus_set()
        else:
            messagebox.showerror("Invalid Name", "Name must be unique and not empty.")

    def remove_selected_player(self):
        selected = self.player_listbox.curselection()
        if selected:
            index = selected[0]
            self.players.pop(index)
            self.player_listbox.delete(index)

    def start_tournament(self):
        if len(self.players) < 2:
            messagebox.showwarning("Not Enough Players", "Add at least 2 players.")
            return
        self.calculate_num_rounds()
        self.setup_round_screen()

    def calculate_num_rounds(self):
        self.num_rounds = 0
        while 2 ** self.num_rounds < len(self.players):
            self.num_rounds += 1

    def setup_round_screen(self):
        self.clear_screen()
        ttk.Label(self.root, text=f"Round {self.round_number}", font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.left_frame = ttk.LabelFrame(main_frame, text="Match Tables", padding=10)
        self.left_frame.pack(side="left", fill="y", expand=True)

        self.right_frame = ttk.LabelFrame(main_frame, text="Match Details", padding=10)
        self.right_frame.pack(side="right", fill="y", padx=(10, 30))

        self.match_listbox = tk.Listbox(self.left_frame, bg="#1e1e1e", fg="white", width=40, height=20, font=("Segoe UI", 10), selectbackground="#444", selectforeground="white", relief="flat", bd=2)
        self.match_listbox.pack()
        self.match_listbox.bind("<<ListboxSelect>>", self.display_match_details)

        if len(self.round_history) < self.round_number:
            self.pair_and_display()
        else:
            self.match_listbox.delete(0, tk.END)
            for i, pair in enumerate(self.current_pairs):
                if pair[1] == "BYE":
                    self.match_listbox.insert(tk.END, f"Table {i+1}: {pair[0].name} receives a BYE")
                else:
                    self.match_listbox.insert(tk.END, f"Table {i+1}: {pair[0].name} vs {pair[1].name}")
            self.match_listbox.select_set(0)
            self.display_match_details(None)
    def display_match_details(self, event):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        index = self.match_listbox.curselection()
        if not index:
            return
        index = index[0]
        if index >= len(self.current_pairs) or self.current_pairs[index][1] == "BYE":
            return

        p1, p2 = self.current_pairs[index]
        data = self.result_data.get(index, {"winner": "", "drop1": False, "drop2": False})

        result_var = tk.StringVar()
        result_var.set(data.get("winner", ""))

        drop1 = tk.BooleanVar()
        drop1.set(data.get("drop1", False))
        drop2 = tk.BooleanVar()
        drop2.set(data.get("drop2", False))

        def update_result():
            self.result_data[index] = {
                "winner": result_var.get(),
                "drop1": drop1.get(),
                "drop2": drop2.get()
            }

        ttk.Label(self.right_frame, text=f"Table {index+1}: {p1.name} vs {p2.name}", font=("Segoe UI", 12, "bold")).pack(pady=5)

        radio_box = ttk.Frame(self.right_frame)
        radio_box.pack(pady=(10, 5))
        ttk.Radiobutton(radio_box, text=f"{p1.name} wins", variable=result_var, value=p1.name, command=update_result).pack(anchor='w', pady=3)
        ttk.Radiobutton(radio_box, text=f"{p2.name} wins", variable=result_var, value=p2.name, command=update_result).pack(anchor='w', pady=3)
        ttk.Radiobutton(radio_box, text="Tie", variable=result_var, value="tie", command=update_result).pack(anchor='w', pady=3)

        ttk.Separator(self.right_frame).pack(fill='x', pady=10)

        drop_box = ttk.Frame(self.right_frame)
        drop_box.pack(pady=(5, 5))
        ttk.Checkbutton(drop_box, text=f"Drop {p1.name}", variable=drop1, command=update_result).pack(anchor='w', pady=4)
        ttk.Checkbutton(drop_box, text=f"Drop {p2.name}", variable=drop2, command=update_result).pack(anchor='w', pady=4)

    def pair_and_display(self):
        self.round_history.append((copy.deepcopy(self.players), copy.deepcopy(self.current_pairs), copy.deepcopy(self.result_data)))
        self.current_pairs = pair_round(self.players)
        #self.result_data.clear()
        #self.match_listbox.delete(0, tk.END)

        for i, pair in enumerate(self.current_pairs):
            if pair[1] == "BYE":
                self.match_listbox.insert(tk.END, f"Table {i+1}: {pair[0].name} receives a BYE")
                pair[0].wins.append("BYE")
                self.result_data[i] = {"winner": "BYE", "drop1": False, "drop2": False}
            else:
                self.match_listbox.insert(tk.END, f"Table {i+1}: {pair[0].name} vs {pair[1].name}")
                self.result_data[i] = {"winner": "", "drop1": False, "drop2": False}

        

    def submit_results(self):
        for i, pair in enumerate(self.current_pairs):
            if pair[1] == "BYE":
                continue
            data = self.result_data.get(i)
            if not data or data["winner"] not in [pair[0].name, pair[1].name, "tie"]:
                messagebox.showerror("Incomplete", f"Missing result for Table {i+1}.")
                return

            winner = data["winner"]
            p1, p2 = pair
            if winner == p1.name:
                p1.wins.append(p2)
                p2.losses.append(p1)
            elif winner == p2.name:
                p2.wins.append(p1)
                p1.losses.append(p2)
            elif winner == "tie":
                p1.ties.append(p2)
                p2.ties.append(p1)

            if data["drop1"]:
                self.drop_player(p1)
            if data["drop2"]:
                self.drop_player(p2)
        
        self.saved_results_history.append(copy.deepcopy(self.result_data))

        self.round_number += 1
        if self.round_number > self.num_rounds:
            messagebox.showinfo("Tournament Complete", "All rounds finished.")
            return
        self.setup_round_screen()

    def drop_player(self, player):
        if player in self.players:
            self.players.remove(player)
            player.name = "#" + player.name
            self.dropped_players.append(player)

    def view_standings(self):
        calculate_standings(self.players)
        win = tk.Toplevel(self.root)
        win.title("Standings")
        win.configure(bg="#2e2e2e")
        ttk.Label(win, text="Standings", font=("Segoe UI", 14, "bold")).pack(pady=10)

        sorted_players = sorted(self.players, key=lambda x: -int(x.tiebreaker))
        for i, p in enumerate(sorted_players):
            ttk.Label(win, text=f"{i+1}. {p.name} - Tiebreaker: {p.tiebreaker}").pack(anchor='w', padx=15, pady=2)

    def undo_last_round(self):
        if self.round_number <= 1 or not self.round_history:
            messagebox.showwarning("Undo Error", "No round to undo.")
            return
        self.round_number -= 1
        self.players, self.current_pairs, self.result_data = self.round_history.pop()
        self.setup_round_screen()
        

        if self.saved_results_history:
            self.result_data = self.saved_results_history.pop()
        self.match_listbox.select_set(0)
        self.display_match_details(None)

        # Restore the UI state of all tables
        for i in range(len(self.current_pairs)):
            if self.current_pairs[i][1] != "BYE":
                self.match_listbox.select_clear(0, tk.END)
                self.match_listbox.select_set(i)
                self.display_match_details(None)

        # Reset view to first match
        self.match_listbox.select_set(0)
        self.display_match_details(None)
    def add_late_player(self):
        name = simpledialog.askstring("Add Late Player", "Enter the player's name:")
        if not name:
            return
        name = name.strip()
        if not name or any(p.name == name for p in self.players):
            messagebox.showerror("Invalid Name", "Name must be unique and non-empty.")
            return
        new_player = Player(name)
        new_player.losses.append("BYE")
        self.players.append(new_player)
        messagebox.showinfo("Player Added", f"{name} has been added with a Round 1 loss.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentGUI(root)
    root.mainloop()
