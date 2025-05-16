import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import json
from main import search_beatmaps, download_beatmap, load_config, save_config, DEFAULT_DOWNLOAD_FOLDER

class OsuDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("osu! Beatmap Downloader")
        self.root.geometry("800x600")
        self.config = load_config()
        self.download_folder = self.config.get("download_folder", DEFAULT_DOWNLOAD_FOLDER)
        self.search_results = []
        self.create_widgets()

    def create_widgets(self):
        # 設定區塊
        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_top, text="下載資料夾:").pack(side=tk.LEFT)
        self.folder_var = tk.StringVar(value=self.download_folder)
        self.folder_entry = ttk.Entry(frame_top, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_top, text="選擇...", command=self.choose_folder).pack(side=tk.LEFT)
        ttk.Button(frame_top, text="儲存設定", command=self.save_folder).pack(side=tk.LEFT, padx=5)

        # 搜尋參數
        frame_params = ttk.LabelFrame(self.root, text="搜尋參數")
        frame_params.pack(fill=tk.X, padx=10, pady=5)
        self.query_var = tk.StringVar()
        self.limit_var = tk.StringVar(value="100")
        self.offset_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.sort_var = tk.StringVar()
        ttk.Label(frame_params, text="關鍵字:").grid(row=0, column=0)
        ttk.Entry(frame_params, textvariable=self.query_var, width=20).grid(row=0, column=1)
        ttk.Label(frame_params, text="數量:").grid(row=0, column=2)
        ttk.Entry(frame_params, textvariable=self.limit_var, width=6).grid(row=0, column=3)
        ttk.Label(frame_params, text="偏移:").grid(row=0, column=4)
        ttk.Entry(frame_params, textvariable=self.offset_var, width=6).grid(row=0, column=5)
        ttk.Label(frame_params, text="狀態:").grid(row=0, column=6)
        ttk.Entry(frame_params, textvariable=self.status_var, width=8).grid(row=0, column=7)
        ttk.Label(frame_params, text="模式:").grid(row=0, column=8)
        ttk.Entry(frame_params, textvariable=self.mode_var, width=8).grid(row=0, column=9)
        ttk.Label(frame_params, text="排序:").grid(row=0, column=10)
        ttk.Entry(frame_params, textvariable=self.sort_var, width=10).grid(row=0, column=11)
        ttk.Button(frame_params, text="搜尋", command=self.start_search).grid(row=0, column=12, padx=5)

        # 結果列表
        frame_results = ttk.LabelFrame(self.root, text="搜尋結果")
        frame_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("id", "set_id", "artist", "title")
        self.tree = ttk.Treeview(frame_results, columns=columns, show="headings", selectmode="extended")
        for col, txt in zip(columns, ["ID", "SetID", "Artist", "Title"]):
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=80 if col!="title" else 250)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 下載控制
        frame_dl = ttk.Frame(self.root)
        frame_dl.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frame_dl, text="下載選取", command=self.start_download_selected).pack(side=tk.LEFT)
        ttk.Button(frame_dl, text="下載全部", command=self.start_download_all).pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(frame_dl, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10)
        self.status_var_gui = tk.StringVar()
        ttk.Label(frame_dl, textvariable=self.status_var_gui, foreground="blue").pack(side=tk.LEFT)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.folder_var.set(folder)

    def save_folder(self):
        folder = self.folder_var.get().strip()
        if folder:
            try:
                os.makedirs(folder, exist_ok=True)
                self.download_folder = folder
                self.config["download_folder"] = folder
                save_config(self.config)
                messagebox.showinfo("成功", f"下載資料夾已更新為: {folder}")
            except Exception as e:
                messagebox.showerror("錯誤", f"設定資料夾失敗: {e}")

    def start_search(self):
        threading.Thread(target=self.search, daemon=True).start()

    def search(self):
        self.status_var_gui.set("搜尋中...")
        self.tree.delete(*self.tree.get_children())
        query = self.query_var.get().strip() or None
        try:
            limit = int(self.limit_var.get())
        except:
            limit = 100
        try:
            offset = int(self.offset_var.get())
        except:
            offset = 0
        status = [int(s.strip()) for s in self.status_var.get().split(',')] if self.status_var.get().strip() else None
        mode = [int(m.strip()) for m in self.mode_var.get().split(',')] if self.mode_var.get().strip() else None
        sort = self.sort_var.get().split(',') if self.sort_var.get().strip() else None
        results = search_beatmaps(query=query, limit=limit, offset=offset, status=status, mode=mode, sort=sort)
        if results:
            if isinstance(results, list):
                beatmaps_list = results
            elif isinstance(results, dict):
                beatmaps_list = results.get('results', results.get('beatmaps', []))
            else:
                self.status_var_gui.set("⚠️ 無法解析回應格式")
                return
            self.search_results = beatmaps_list
            for bm in beatmaps_list:
                beatmap_id = bm.get('id')
                beatmapset_id = bm.get('beatmapset_id', bm.get('id'))
                artist = bm.get('artist', 'Unknown Artist')
                title = bm.get('title', 'Unknown Title')
                self.tree.insert('', 'end', values=(beatmap_id, beatmapset_id, artist, title))
            self.status_var_gui.set(f"找到 {len(beatmaps_list)} 張圖譜")
        else:
            self.status_var_gui.set("❌ 搜尋失敗或無結果")

    def start_download_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先選取要下載的圖譜！")
            return
        indices = [self.tree.index(item) for item in selected]
        self.start_download(indices)

    def start_download_all(self):
        if not self.search_results:
            messagebox.showwarning("提示", "請先搜尋圖譜！")
            return
        indices = list(range(len(self.search_results)))
        self.start_download(indices)

    def start_download(self, indices):
        threading.Thread(target=self.download, args=(indices,), daemon=True).start()

    def download(self, indices):
        self.progress["maximum"] = len(indices)
        self.progress["value"] = 0
        for idx, i in enumerate(indices):
            bm = self.search_results[i]
            beatmapset_id = bm.get('beatmapset_id', bm.get('id'))
            artist = bm.get('artist', 'Unknown Artist')
            title = bm.get('title', 'Unknown Title')
            self.status_var_gui.set(f"下載中: {artist} - {title}")
            ok = download_beatmap(beatmapset_id, f"{artist} - {title}", self.download_folder)
            self.progress["value"] = idx + 1
            self.root.update_idletasks()
            if not ok:
                messagebox.showerror("下載失敗", f"無法下載: {artist} - {title}")
        self.status_var_gui.set("下載完成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = OsuDownloaderGUI(root)
    root.mainloop()