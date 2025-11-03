import tkinter as tk
from tkinter import scrolledtext, font
import feedparser
import pyttsx3

# URL RSS feed từ BBC News
RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

# Hàm lấy tin tức
def fetch_news():
    feed = feedparser.parse(RSS_URL)
    news_list.delete(0, tk.END)  # xóa danh sách cũ
    articles.clear()
    for entry in feed.entries[:20]:  # lấy 20 tin đầu
        # Một số RSS chỉ có summary, một số có content
        content = entry.get("summary", "")
        if "content" in entry:
            content = entry.content[0].value
        articles.append((entry.title, content))
        news_list.insert(tk.END, entry.title)

# Hàm hiển thị nội dung tin
def show_article(event):
    selection = news_list.curselection()
    if not selection:
        return
    index = selection[0]
    title, content = articles[index]
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"{title}\n\n{content}")

# Hàm đọc bài báo (đọc toàn bộ text trong khung hiển thị)
def read_article():
    # Khởi tạo TTS engine
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # tốc độ đọc
    engine.setProperty("voice", engine.getProperty("voices")[1].id)  # giọng nữ (0 = nam, 1 = nữ)

    text = text_area.get(1.0, tk.END).strip()
    if text:
        engine.say(text)
        engine.runAndWait()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("English News Reader")
root.geometry("900x800")

articles = []

# Load font Livvic (nếu không có thì fallback Arial)
try:
    livvic_font = font.Font(family="Livvic", size=14)
except:
    livvic_font = font.Font(family="Arial", size=14)

# Danh sách tin tức
news_list = tk.Listbox(root, width=40, height=20, font=livvic_font)
news_list.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
news_list.bind("<<ListboxSelect>>", show_article)

# Nội dung bài báo
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=livvic_font)
text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Nút điều khiển
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=10)

fetch_btn = tk.Button(button_frame, text="🔄 Refresh News", command=fetch_news, font=livvic_font)
fetch_btn.pack(side=tk.LEFT, padx=5)

read_btn = tk.Button(button_frame, text="🔊 Read Article", command=read_article, font=livvic_font)
read_btn.pack(side=tk.LEFT, padx=5)

# Lấy tin tức ban đầu
fetch_news()

root.mainloop()
