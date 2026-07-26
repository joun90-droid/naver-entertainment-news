import os
import sys
import json
import time
import webbrowser
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from crawler import NaverEntertainCrawler

# Set high DPI awareness on Windows if available
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class NaverEntertainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("네이버 연예뉴스 핫토픽 (실시간 100% 연동) | NAVER Entertain Hot Topic")
        self.root.geometry("1240x840")
        self.root.minsize(1050, 680)
        self.root.configure(bg="#0f172a")

        # App state
        self.crawler = NaverEntertainCrawler()
        self.current_category = "실시간 랭킹"
        self.current_news_items = []
        self.filtered_news_items = []
        self.selected_item = None
        self.bookmarks = self.load_bookmarks()
        self.executor = ThreadPoolExecutor(max_workers=6)

        # Default 15s auto-refresh for zero-click live sync
        self.auto_refresh_sec = 15
        self.refresh_timer_id = None
        self.tk_images = {}

        self.setup_styles()
        self.build_ui()
        
        # Load initial category data & start automatic 15s sync loop
        self.load_category(self.current_category)
        self.schedule_auto_refresh()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        self.BG_MAIN = "#0f172a"
        self.BG_CARD = "#1e293b"
        self.BG_CARD_HOVER = "#334155"
        self.BG_PANEL = "#1e293b"
        self.ACCENT_PURPLE = "#8b5cf6"
        self.ACCENT_PINK = "#ec4899"
        self.TEXT_PRIMARY = "#f8fafc"
        self.TEXT_MUTED = "#94a3b8"
        self.BORDER_COLOR = "#334155"

        style.configure("TFrame", background=self.BG_MAIN)
        style.configure("Card.TFrame", background=self.BG_CARD, relief="flat")
        style.configure("Header.TFrame", background="#0b0f19")
        style.configure("Status.TFrame", background="#0b0f19")
        style.configure("Vertical.TScrollbar", background="#334155", troughcolor=self.BG_MAIN, borderwidth=0, arrowsize=12)

    def build_ui(self):
        # 1. Header Frame
        header = tk.Frame(self.root, bg="#0b0f19", height=70)
        header.pack(fill="x", side="top")

        title_box = tk.Frame(header, bg="#0b0f19")
        title_box.pack(side="left", padx=20, pady=12)

        title_lbl = tk.Label(
            title_box, 
            text="🎬 네이버 연예뉴스 핫토픽 (100% 실시간 자동 연동)", 
            font=("Malgun Gothic", 16, "bold"), 
            fg="#f472b6", 
            bg="#0b0f19"
        )
        title_lbl.pack(side="top", anchor="w")

        subtitle_lbl = tk.Label(
            title_box, 
            text="새로고침을 누를 필요 없이 실시간으로 네이버 최신 연예뉴스가 갱신됩니다.", 
            font=("Malgun Gothic", 9), 
            fg="#94a3b8", 
            bg="#0b0f19"
        )
        subtitle_lbl.pack(side="top", anchor="w")

        # Top Control Buttons
        ctrl_box = tk.Frame(header, bg="#0b0f19")
        ctrl_box.pack(side="right", padx=20, pady=15)

        # Refresh button
        btn_refresh = tk.Button(
            ctrl_box,
            text="🔄 즉시 수신",
            font=("Malgun Gothic", 10, "bold"),
            fg="#ffffff",
            bg="#8b5cf6",
            activebackground="#7c3aed",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.on_manual_refresh
        )
        btn_refresh.pack(side="left", padx=5)

        # Export button
        btn_export = tk.Button(
            ctrl_box,
            text="📥 내보내기",
            font=("Malgun Gothic", 10, "bold"),
            fg="#ffffff",
            bg="#3b82f6",
            activebackground="#2563eb",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.export_news_data
        )
        btn_export.pack(side="left", padx=5)

        # Auto refresh selector
        tk.Label(ctrl_box, text="자동 갱신:", font=("Malgun Gothic", 9), fg="#94a3b8", bg="#0b0f19").pack(side="left", padx=(10, 5))
        self.auto_refresh_var = tk.StringVar(value="15초")
        refresh_options = ["10초", "15초", "30초", "OFF"]
        opt_menu = ttk.OptionMenu(ctrl_box, self.auto_refresh_var, "15초", *refresh_options, command=self.on_auto_refresh_change)
        opt_menu.pack(side="left")

        # 2. Category Tab Navigation Bar
        nav_bar = tk.Frame(self.root, bg="#1e293b", height=45)
        nav_bar.pack(fill="x", side="top")

        self.tab_buttons = {}
        category_list = ["실시간 랭킹", "연예가 핫토픽", "방송·TV", "영화", "드라마", "뮤직", "해외연예", "⭐ 즐겨찾기"]
        
        for cat in category_list:
            btn = tk.Button(
                nav_bar,
                text=cat,
                font=("Malgun Gothic", 10, "bold" if cat == self.current_category else "normal"),
                fg="#f8fafc" if cat == self.current_category else "#94a3b8",
                bg="#8b5cf6" if cat == self.current_category else "#1e293b",
                activebackground="#7c3aed",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=16,
                pady=8,
                cursor="hand2",
                command=lambda c=cat: self.select_category(c)
            )
            btn.pack(side="left", fill="y", padx=1)
            self.tab_buttons[cat] = btn

        # Search Bar Subframe
        search_bar = tk.Frame(self.root, bg="#0f172a", pady=10, padx=20)
        search_bar.pack(fill="x", side="top")

        search_inner = tk.Frame(search_bar, bg="#1e293b", bd=1, relief="solid")
        search_inner.pack(side="left", fill="x", expand=True)

        tk.Label(search_inner, text="  🔍 ", font=("Malgun Gothic", 11), fg="#94a3b8", bg="#1e293b").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_news())
        search_entry = tk.Entry(
            search_inner,
            textvariable=self.search_var,
            font=("Malgun Gothic", 11),
            fg="#f8fafc",
            bg="#1e293b",
            insertbackground="#f8fafc",
            relief="flat",
            bd=0
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)

        btn_clear_search = tk.Button(
            search_inner,
            text="✕",
            font=("Malgun Gothic", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda: self.search_var.set("")
        )
        btn_clear_search.pack(side="right", padx=8)

        # 3. Main Content Split View
        main_split = tk.Frame(self.root, bg=self.BG_MAIN)
        main_split.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # 3-A. Left News Feed List
        left_container = tk.Frame(main_split, bg=self.BG_MAIN)
        left_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(left_container, bg=self.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.canvas.yview)
        
        self.feed_frame = tk.Frame(self.canvas, bg=self.BG_MAIN)
        self.feed_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.feed_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 3-B. Right Inspector & Detail Panel
        self.right_panel = tk.Frame(main_split, bg="#1e293b", width=420, bd=1, relief="solid")
        self.right_panel.pack(side="right", fill="both", expand=False)
        self.right_panel.pack_propagate(False)

        self.build_inspector_panel()

        # 4. Bottom Status Bar
        status_bar = tk.Frame(self.root, bg="#0b0f19", height=30)
        status_bar.pack(fill="x", side="bottom")

        self.status_label = tk.Label(
            status_bar, 
            text=" 🟢 100% 실시간 자동 연동 활성화 (15초 마다 자동 수신)", 
            font=("Malgun Gothic", 9), 
            fg="#4ade80", 
            bg="#0b0f19"
        )
        self.status_label.pack(side="left", padx=15, pady=4)

        self.update_time_label = tk.Label(
            status_bar, 
            text="마지막 업데이트: - ", 
            font=("Malgun Gothic", 9), 
            fg="#64748b", 
            bg="#0b0f19"
        )
        self.update_time_label.pack(side="right", padx=15, pady=4)

    def build_inspector_panel(self):
        ins_header = tk.Frame(self.right_panel, bg="#0f172a", pady=10, padx=15)
        ins_header.pack(fill="x", side="top")

        tk.Label(ins_header, text="📌 기사 상세보기", font=("Malgun Gothic", 12, "bold"), fg="#f472b6", bg="#0f172a").pack(anchor="w")

        self.ins_container = tk.Frame(self.right_panel, bg="#1e293b", padx=15, pady=15)
        self.ins_container.pack(fill="both", expand=True)

        self.preview_img_lbl = tk.Label(self.ins_container, bg="#0f172a", text="[ 썸네일 이미지 ]", fg="#64748b", font=("Malgun Gothic", 10))
        self.preview_img_lbl.pack(fill="x", pady=(0, 12))

        badge_frame = tk.Frame(self.ins_container, bg="#1e293b")
        badge_frame.pack(fill="x", anchor="w", pady=(0, 8))

        self.lbl_office_badge = tk.Label(badge_frame, text="", font=("Malgun Gothic", 9, "bold"), fg="#8b5cf6", bg="#2e1065", padx=8, pady=2)
        self.lbl_office_badge.pack(side="left", padx=(0, 6))

        self.lbl_cat_badge = tk.Label(badge_frame, text="", font=("Malgun Gothic", 9), fg="#ec4899", bg="#831843", padx=8, pady=2)
        self.lbl_cat_badge.pack(side="left")

        self.ins_title_lbl = tk.Label(
            self.ins_container,
            text="목록에서 기사를 선택하세요",
            font=("Malgun Gothic", 13, "bold"),
            fg="#f8fafc",
            bg="#1e293b",
            wraplength=370,
            justify="left"
        )
        self.ins_title_lbl.pack(anchor="w", fill="x", pady=(0, 12))

        summary_frame = tk.Frame(self.ins_container, bg="#0f172a", padx=12, pady=10)
        summary_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.ins_summary_text = tk.Text(
            summary_frame,
            font=("Malgun Gothic", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            relief="flat",
            wrap="word",
            bd=0
        )
        self.ins_summary_text.pack(fill="both", expand=True)

        actions_box = tk.Frame(self.ins_container, bg="#1e293b")
        actions_box.pack(fill="x", side="bottom")

        self.btn_open_browser = tk.Button(
            actions_box,
            text="🌐 원본 기사 읽기 (웹 브라우저)",
            font=("Malgun Gothic", 10, "bold"),
            fg="#ffffff",
            bg="#ec4899",
            activebackground="#db2777",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            pady=9,
            cursor="hand2",
            command=self.open_article_in_browser
        )
        self.btn_open_browser.pack(fill="x", pady=(0, 6))

        sub_actions = tk.Frame(actions_box, bg="#1e293b")
        sub_actions.pack(fill="x")

        self.btn_bookmark = tk.Button(
            sub_actions,
            text="⭐ 즐겨찾기",
            font=("Malgun Gothic", 9, "bold"),
            fg="#f8fafc",
            bg="#334155",
            activebackground="#475569",
            relief="flat",
            bd=0,
            pady=6,
            cursor="hand2",
            command=self.toggle_bookmark
        )
        self.btn_bookmark.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_copy_link = tk.Button(
            sub_actions,
            text="📋 링크 복사",
            font=("Malgun Gothic", 9, "bold"),
            fg="#f8fafc",
            bg="#334155",
            activebackground="#475569",
            relief="flat",
            bd=0,
            pady=6,
            cursor="hand2",
            command=self.copy_link_to_clipboard
        )
        self.btn_copy_link.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def select_category(self, category):
        self.current_category = category
        for cat, btn in self.tab_buttons.items():
            if cat == category:
                btn.configure(bg="#8b5cf6", fg="#ffffff", font=("Malgun Gothic", 10, "bold"))
            else:
                btn.configure(bg="#1e293b", fg="#94a3b8", font=("Malgun Gothic", 10, "normal"))

        self.search_var.set("")
        if category == "⭐ 즐겨찾기":
            self.load_bookmarks_feed()
        else:
            self.load_category(category)

    def load_category(self, category_name):
        def background_fetch():
            items = self.crawler.fetch_category(category_name)
            self.root.after(0, lambda: self.render_feed(items, category_name))

        threading.Thread(target=background_fetch, daemon=True).start()

    def render_feed(self, items, category_name):
        self.current_news_items = items
        self.filtered_news_items = items
        
        for child in self.feed_frame.winfo_children():
            child.destroy()

        if not items:
            empty_lbl = tk.Label(
                self.feed_frame,
                text="표시할 뉴스 기사가 없거나 네트워크 수신 중입니다...",
                font=("Malgun Gothic", 11),
                fg="#94a3b8",
                bg=self.BG_MAIN,
                pady=40
            )
            empty_lbl.pack()
            return

        now_str = datetime.now().strftime("%H:%M:%S")
        self.status_label.configure(text=f" 🟢 [{category_name}] 실시간 자동 수신 완료 (총 {len(items)}개 항목)", fg="#4ade80")
        self.update_time_label.configure(text=f"마지막 업데이트: {now_str}")

        for idx, item in enumerate(items):
            card = self.create_news_card(self.feed_frame, item, idx + 1)
            card.pack(fill="x", pady=4, padx=2)

        if items and (not self.selected_item or not any(it['id'] == self.selected_item['id'] for it in items)):
            self.inspect_article(items[0])

    def create_news_card(self, parent, item, rank_num):
        card = tk.Frame(parent, bg="#1e293b", bd=1, relief="solid", cursor="hand2")

        badge_bg = "#ec4899" if rank_num <= 3 else "#334155"
        rank_lbl = tk.Label(
            card,
            text=str(rank_num),
            font=("Malgun Gothic", 11, "bold"),
            fg="#ffffff",
            bg=badge_bg,
            width=3,
            pady=4
        )
        rank_lbl.pack(side="left", fill="y", padx=(0, 10))

        thumb_lbl = tk.Label(card, text="🖼️", font=("Segoe UI Emoji", 14), bg="#0f172a", fg="#64748b", width=12, height=4)
        thumb_lbl.pack(side="left", padx=(0, 10), pady=6)

        if item.get("thumbnail"):
            def load_thumb(u=item["thumbnail"], lbl=thumb_lbl):
                img = self.crawler.fetch_image(u, size=(110, 75))
                if img:
                    photo = ImageTk.PhotoImage(img)
                    def update_ui():
                        if lbl.winfo_exists():
                            lbl.configure(image=photo, text="", width=110, height=75)
                            self.tk_images[u] = photo
                    self.root.after(0, update_ui)
            self.executor.submit(load_thumb)

        content_box = tk.Frame(card, bg="#1e293b")
        content_box.pack(side="left", fill="both", expand=True, pady=8, padx=(0, 10))

        top_meta = tk.Frame(content_box, bg="#1e293b")
        top_meta.pack(fill="x", anchor="w")

        office_lbl = tk.Label(
            top_meta, 
            text=f"[{item['office']}]", 
            font=("Malgun Gothic", 9, "bold"), 
            fg="#c084fc", 
            bg="#1e293b"
        )
        office_lbl.pack(side="left")

        if self.is_bookmarked(item):
            bm_lbl = tk.Label(top_meta, text="⭐ 즐겨찾기됨", font=("Malgun Gothic", 8, "bold"), fg="#facc15", bg="#1e293b")
            bm_lbl.pack(side="left", padx=8)

        title_lbl = tk.Label(
            content_box,
            text=item['title'],
            font=("Malgun Gothic", 11, "bold"),
            fg="#f8fafc",
            bg="#1e293b",
            anchor="w",
            justify="left",
            wraplength=600
        )
        title_lbl.pack(fill="x", anchor="w", pady=(2, 2))

        summary_lbl = tk.Label(
            content_box,
            text=item['summary'],
            font=("Malgun Gothic", 9),
            fg="#94a3b8",
            bg="#1e293b",
            anchor="w",
            justify="left",
            wraplength=600
        )
        summary_lbl.pack(fill="x", anchor="w")

        elements = [card, rank_lbl, thumb_lbl, content_box, top_meta, office_lbl, title_lbl, summary_lbl]
        for elem in elements:
            elem.bind("<Button-1>", lambda e, it=item: self.inspect_article(it))
            elem.bind("<Enter>", lambda e, c=card: c.configure(bg="#334155"))
            elem.bind("<Leave>", lambda e, c=card: c.configure(bg="#1e293b"))

        return card

    def inspect_article(self, item):
        self.selected_item = item

        self.ins_title_lbl.configure(text=item['title'])
        self.lbl_office_badge.configure(text=item['office'])
        self.lbl_cat_badge.configure(text=item.get('category', self.current_category))

        self.ins_summary_text.delete("1.0", tk.END)
        summary_body = item['summary']
        if not summary_body or summary_body == item['title']:
            summary_body = "(요약 본문이 없습니다. 전체 내용은 원본 기사 읽기를 참조하세요.)"
        self.ins_summary_text.insert(tk.END, f"{summary_body}\n\n🔗 기사 URL:\n{item['url']}")

        if self.is_bookmarked(item):
            self.btn_bookmark.configure(text="★ 즐겨찾기 해제", fg="#facc15", bg="#422006")
        else:
            self.btn_bookmark.configure(text="⭐ 즐겨찾기 추가", fg="#f8fafc", bg="#334155")

        if item.get("thumbnail"):
            def load_preview_img():
                img = self.crawler.fetch_image(item["thumbnail"], size=(370, 240))
                if img:
                    photo = ImageTk.PhotoImage(img)
                    def update_preview():
                        if self.preview_img_lbl.winfo_exists():
                            self.preview_img_lbl.configure(image=photo, text="", height=240)
                            self.tk_images['preview'] = photo
                    self.root.after(0, update_preview)
            self.executor.submit(load_preview_img)
        else:
            self.preview_img_lbl.configure(image="", text="[ 썸네일 이미지 없음 ]", height=100)

    def filter_news(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.filtered_news_items = self.current_news_items
        else:
            self.filtered_news_items = [
                it for it in self.current_news_items 
                if query in it['title'].lower() or query in it['office'].lower() or query in it['summary'].lower()
            ]

        for child in self.feed_frame.winfo_children():
            child.destroy()

        if not self.filtered_news_items:
            empty_lbl = tk.Label(
                self.feed_frame,
                text=f"'{query}' 검색 결과가 없습니다.",
                font=("Malgun Gothic", 11),
                fg="#94a3b8",
                bg=self.BG_MAIN,
                pady=40
            )
            empty_lbl.pack()
            return

        for idx, item in enumerate(self.filtered_news_items):
            card = self.create_news_card(self.feed_frame, item, idx + 1)
            card.pack(fill="x", pady=4, padx=2)

    def open_article_in_browser(self):
        if self.selected_item and self.selected_item.get('url'):
            webbrowser.open(self.selected_item['url'])
            self.status_label.configure(text=f" 🌐 웹 브라우저 연결: {self.selected_item['title'][:30]}...", fg="#60a5fa")

    def copy_link_to_clipboard(self):
        if self.selected_item and self.selected_item.get('url'):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected_item['url'])
            self.status_label.configure(text=" 📋 기사 링크가 클립보드에 복사되었습니다!", fg="#facc15")

    def load_bookmarks(self):
        filepath = "bookmarks.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_bookmarks(self):
        filepath = "bookmarks.json"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Failed to save bookmarks:", e)

    def is_bookmarked(self, item):
        return item['id'] in self.bookmarks

    def toggle_bookmark(self):
        if not self.selected_item:
            return
        item = self.selected_item
        item_id = item['id']
        
        if item_id in self.bookmarks:
            del self.bookmarks[item_id]
            self.status_label.configure(text=" ★ 즐겨찾기에서 제거되었습니다.", fg="#94a3b8")
        else:
            self.bookmarks[item_id] = item
            self.status_label.configure(text=" ⭐ 즐겨찾기에 추가되었습니다!", fg="#facc15")
        
        self.save_bookmarks()
        self.inspect_article(item)

        if self.current_category == "⭐ 즐겨찾기":
            self.load_bookmarks_feed()

    def load_bookmarks_feed(self):
        items = list(self.bookmarks.values())
        self.render_feed(items, "⭐ 즐겨찾기")

    def export_news_data(self):
        if not self.current_news_items:
            messagebox.showinfo("안내", "내보낼 뉴스 기사가 없습니다.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file (*.txt)", "*.txt"), ("JSON file (*.json)", "*.json"), ("CSV file (*.csv)", "*.csv")],
            title="연예뉴스 핫토픽 데이터 저장"
        )
        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.current_news_items, f, ensure_ascii=False, indent=2)
            elif ext == ".csv":
                import csv
                with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["순위", "언론사", "제목", "요약", "URL"])
                    for item in self.current_news_items:
                        writer.writerow([item.get('rank', ''), item.get('office', ''), item.get('title', ''), item.get('summary', ''), item.get('url', '')])
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"=== 네이버 연예뉴스 [{self.current_category}] 핫토픽 목록 ===\n")
                    f.write(f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for item in self.current_news_items:
                        f.write(f"[{item.get('rank', '')}] [{item.get('office', '')}] {item.get('title', '')}\n")
                        f.write(f"요약: {item.get('summary', '')}\n")
                        f.write(f"URL: {item.get('url', '')}\n")
                        f.write("-" * 60 + "\n")

            messagebox.showinfo("성공", f"파일이 성공적으로 저장되었습니다:\n{file_path}")
            self.status_label.configure(text=f" 💾 데이터가 저장되었습니다: {os.path.basename(file_path)}", fg="#4ade80")
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다: {e}")

    def on_manual_refresh(self):
        if self.current_category == "⭐ 즐겨찾기":
            self.load_bookmarks_feed()
        else:
            self.load_category(self.current_category)

    def on_auto_refresh_change(self, val):
        sec_map = {"10초": 10, "15초": 15, "30초": 30, "OFF": 0}
        self.auto_refresh_sec = sec_map.get(val, 0)
        self.schedule_auto_refresh()

    def schedule_auto_refresh(self):
        if self.refresh_timer_id:
            self.root.after_cancel(self.refresh_timer_id)
            self.refresh_timer_id = None

        if self.auto_refresh_sec > 0:
            self.refresh_timer_id = self.root.after(self.auto_refresh_sec * 1000, self.auto_refresh_trigger)

    def auto_refresh_trigger(self):
        if self.current_category != "⭐ 즐겨찾기":
            self.load_category(self.current_category)
        self.schedule_auto_refresh()
