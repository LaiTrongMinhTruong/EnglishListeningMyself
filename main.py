import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext, font
import threading
import json, os, wave, base64
from datetime import datetime
import numpy as np
import pyttsx3
from deep_translator import GoogleTranslator
from openai import OpenAI
import sounddevice as sd
import speech_recognition as sr
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

APP_DIR = os.path.join(os.environ["APPDATA"], "EnglishStudyBox") #thay vì lưu vào vocab.json trong thư mục này, khi nén sẽ bị mất dữ liệu khi chạy, đoạn code này sẽ lưu từ vựng vào appdata để không mất dữ liệu (trường hợp nén vào .exe)
os.makedirs(APP_DIR, exist_ok=True)

FONT_FILE = resource_path("Livvic-Regular.ttf")
VOCAB_FILE = os.path.join(APP_DIR, "vocab.json")
# VOCAB_FILE = "vocab.json" #nếu bạn không có ý định nén thành file exe
RECORDINGS_DIR = "recordings"
#if you use better model for audio eval, uncomment this line below:
# os.makedirs(RECORDINGS_DIR, exist_ok=True)


recording = False
recorded_frames = []
stream = None


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set in environment. AI functions will fail until set.")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


root = tk.Tk()
root.title("🎓 English Study Box")
root.config(bg="#f8f9fa")
# root.geometry('1000x1000')
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

try:
    livvic_font = font.Font(family="Livvic", size=13)
except Exception:
    livvic_font = font.Font(family="Arial", size=13)

TITLE_BG = "#f8f9fa"
CARD_BG = "#ffffff"
ACCENT = "#3498db"
BTN_GREEN = "#2ecc71"
TEXT_BG = "#fafafa"

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1, uniform="group_root")
root.grid_columnconfigure(1, weight=1, uniform="group_root")


def read_text(text):
    if not text:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id if len(voices) > 1 else voices[0].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS error:", e)

def translate_text(from_lang, to_lang, text):
    if not text.strip():
        return ""
    src_code = "vi" if from_lang in ("vn","vi") else "en"
    tgt_code = "vi" if to_lang in ("vn","vi") else "en"
    try:
        return GoogleTranslator(source=src_code, target=tgt_code).translate(text)
    except Exception as e:
        return f"[Translate error: {e}]"


def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return []
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_vocab(data_list):
    try:
        with open(VOCAB_FILE, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Save vocab error:", e)
        return False


# Left frame (translation top, vocab bottom)
left_frame = tk.Frame(root, bg=TITLE_BG)
left_frame.grid(row=0, column=0, sticky="nsew", padx=(20,10), pady=20)
left_frame.grid_rowconfigure(0, weight=2, uniform="group_top_left")
left_frame.grid_rowconfigure(1, weight=3, uniform="group_top_left")
left_frame.grid_columnconfigure(0, weight=1, uniform="group_top_left")

# Translation Box (top)
trans_block = tk.Frame(left_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
trans_block.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0,8))
trans_block.grid_columnconfigure(0, weight=1)
trans_block.grid_columnconfigure(1, weight=0)
trans_block.grid_columnconfigure(2, weight=1)
trans_block.grid_rowconfigure(0, weight=1)

left_trans_area = scrolledtext.ScrolledText(trans_block, wrap=tk.WORD, font=livvic_font, bg=TEXT_BG, padx=10, pady=10)
left_trans_area.grid(row=0, column=0, sticky="nsew", padx=(12,6), pady=12)

mid_btns = tk.Frame(trans_block, bg=CARD_BG)
mid_btns.grid(row=0, column=1, sticky="ns", padx=6, pady=12)
#add row configure to mid_btns
mid_btns.grid_rowconfigure(0, weight=1, uniform="group_mid_btns")
mid_btns.grid_rowconfigure(1, weight=1, uniform="group_mid_btns")
mid_btns.grid_rowconfigure(2, weight=1, uniform="group_mid_btns")
mid_btns.grid_rowconfigure(3, weight=1, uniform="group_mid_btns")
mid_btns.grid_rowconfigure(4, weight=1, uniform="group_mid_btns")
mid_btns.grid_rowconfigure(5, weight=1, uniform="group_mid_btns")

right_trans_area = scrolledtext.ScrolledText(trans_block, wrap=tk.WORD, font=livvic_font, bg=TEXT_BG, padx=10, pady=10)
right_trans_area.grid(row=0, column=2, sticky="nsew", padx=(6,12), pady=12)

def do_translate_left_to_right():
    src = left_trans_area.get(1.0, tk.END).strip()
    if not src:
        left_trans_area.insert(tk.END, "\n⚠️ Nothing to translate.")
        return
    tgt = translate_text("vn","en", src)
    right_trans_area.delete(1.0, tk.END)
    right_trans_area.insert(tk.END, tgt)

def do_translate_right_to_left():
    src = right_trans_area.get(1.0, tk.END).strip()
    if not src:
        right_trans_area.insert(tk.END, "\n⚠️ Nothing to translate.")
        return
    tgt = translate_text("en","vn", src)
    left_trans_area.delete(1.0, tk.END)
    left_trans_area.insert(tk.END, tgt)

def do_read_right():
    read_text(right_trans_area.get(1.0, tk.END).strip())


def _first_non_empty_line(text: str) -> str:
    if not text:
        return ""
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s
    return ""

#add word to vocab func
def add_translation_to_vocab():
    vn_full = left_trans_area.get(1.0, tk.END)
    en_full = right_trans_area.get(1.0, tk.END)
    vn = _first_non_empty_line(vn_full)
    en = _first_non_empty_line(en_full)
    if not vn and not en:
        messagebox.showinfo("Info", "There is no content to add. Please enter Vietnamese and English text.")
        return
    if not vn:
        messagebox.showinfo("Info", "Cannot find Vietnamese text in the left area.")
        return
    if not en:
        messagebox.showinfo("Info", "Cannot find English translation in the right area.")
        return
    # Insert VN as 'word' and EN as 'meaning' (keeps the pair together)
    tree.insert("", "end", values=(en, vn, ""))
    # save immediately
    save_table_to_file()


def toggle_record_for_area(language, target_text_widget, btn_widget=None):
    global recording, recorded_frames, stream
    lang_code = "vi-VN" if language == "vi" else "en-US"
    if not recording:
        try:
            recording = True
            recorded_frames = []
            def callback(indata, frames, time, status):
                if recording:
                    recorded_frames.append(indata.copy())
            stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback)
            stream.start()
            if btn_widget:
                btn_widget.config(text="Stop Recording")
            # target_text_widget.insert(tk.END, "\n🎙️ Recording... Speak now.")
        except Exception as e:
            recording = False
            if btn_widget:
                btn_widget.config(text="Record" + (" VN" if language=="vi" else " EN"))
            # target_text_widget.insert(tk.END, f"\nFailed to start recording: {e}")
    else:
        # stop
        recording = False
        if stream:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass
            stream = None

        if not recorded_frames:
            # target_text_widget.insert(tk.END, "\nNo audio recorded.")
            if btn_widget:
                btn_widget.config(text="Record" + (" VN" if language=="vi" else " EN"))
            return

        audio_data = np.concatenate(recorded_frames, axis=0)
        audio_bytes = audio_data.tobytes()
        sample_width = audio_data.dtype.itemsize
        audio = sr.AudioData(audio_bytes, 16000, sample_width)
        r = sr.Recognizer()
        try:
            text = r.recognize_google(audio, language=lang_code)
            target_text_widget.delete(1.0, tk.END)
            target_text_widget.insert(tk.END, text)
        except sr.UnknownValueError:
            target_text_widget.insert(tk.END, "\n")
        # except Exception as e:
            # target_text_widget.insert(tk.END, f"\nSpeech recognition error: {e}")

        if btn_widget:
            btn_widget.config(text="Record" + (" VN" if language=="vi" else " EN"))

# translation middle buttons
trans_vn_btn = tk.Button(mid_btns, text="VN → EN", font=livvic_font, bg=BTN_GREEN, fg="white", width=12, relief="flat", command=do_translate_left_to_right)
trans_vn_btn.grid(row=0, column=0, sticky="nsew", padx=6, pady=2)

trans_en_btn =tk.Button(mid_btns, text="VN ← EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat", command=do_translate_right_to_left)
trans_en_btn.grid(row=1, column=0, sticky="nsew", padx=6, pady=2)

read_en = tk.Button(mid_btns, text="Read EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat", command=do_read_right)
read_en.grid(row=2, column=0, sticky="nsew", padx=6, pady=2)
# record buttons for VN / EN
rec_vn_btn = tk.Button(mid_btns, text="Record VN", font=livvic_font, bg=BTN_GREEN, fg="white", width=12, relief="flat",
                       command=lambda: toggle_record_for_area("vi", left_trans_area, rec_vn_btn))
# rec_vn_btn.pack(pady=6)
rec_vn_btn.grid(row=3, column=0, sticky="nsew", padx=6, pady=2)
rec_en_btn = tk.Button(mid_btns, text="Record EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat",
                       command=lambda: toggle_record_for_area("en", right_trans_area, rec_en_btn))
# rec_en_btn.pack(pady=6)
rec_en_btn.grid(row=4, column=0, sticky="nsew", padx=6, pady=2)

# button to add current VN/EN pair into vocab notes
add_note_btn = tk.Button(mid_btns, text="Add Vocab", font=livvic_font, bg="#f39c12", fg="white", width=12, relief="flat", command=add_translation_to_vocab)
add_note_btn.grid(row=5, column=0, sticky="nsew", padx=6, pady=2)


vocab_card = tk.Frame(left_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
vocab_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=(8,0))
vocab_card.grid_rowconfigure(0, weight=1)
vocab_card.grid_rowconfigure(1, weight=0)
vocab_card.grid_columnconfigure(0, weight=1)

# Treeview (show data)
cols = ("word", "meaning", "example")
tree_frame = tk.Frame(vocab_card, bg=CARD_BG)
tree_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
for c in cols:
    tree.heading(c, text=c.capitalize())
    tree.column(c, width=200, anchor="w")
tree.grid(row=0, column=0, sticky="nsew")

scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)
scroll_y.grid(row=0, column=1, sticky="ns")

# inline edit: on double click open Entry overlay
editing_entry = None
editing_info = None  # (item_id, col)

def on_tree_double_click(event):
    global editing_entry, editing_info
    region = tree.identify("region", event.x, event.y)
    if region != "cell":
        return
    rowid = tree.identify_row(event.y)
    col = tree.identify_column(event.x)  # like '#1'
    col_index = int(col.replace("#","")) - 1
    if not rowid:
        return
    x,y,width,height = tree.bbox(rowid, column=col)
    value = tree.item(rowid, "values")[col_index]
    editing_info = (rowid, col_index)
    editing_entry = tk.Entry(tree_frame, font=livvic_font)
    editing_entry.insert(0, value)
    editing_entry.place(x=x, y=y, width=width, height=height)
    editing_entry.focus_set()
    def finish_edit(event=None):
        global editing_entry, editing_info
        newval = editing_entry.get()
        item, idx = editing_info
        vals = list(tree.item(item, "values"))
        vals[idx] = newval
        tree.item(item, values=vals)
        editing_entry.destroy()
        editing_entry = None
        editing_info = None
    editing_entry.bind("<Return>", finish_edit)
    editing_entry.bind("<FocusOut>", finish_edit)

tree.bind("<Double-1>", on_tree_double_click)

# buttons under the table
btns_frame = tk.Frame(vocab_card, bg=CARD_BG)
btns_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(6,12))
btns_frame.grid_columnconfigure(0, weight=1)
btns_frame.grid_columnconfigure(1, weight=1)
btns_frame.grid_columnconfigure(2, weight=1)
btns_frame.grid_columnconfigure(3, weight=1)
btns_frame.grid_columnconfigure(4, weight=1)
btns_frame.grid_rowconfigure(0, weight=1)

def refresh_vocab_table():
    tree.delete(*tree.get_children())
    data = load_vocab()
    for entry in data:
        tree.insert("", "end", values=(entry.get("word",""), entry.get("meaning",""), entry.get("example","")))
    # autosize columns a bit
    for c in cols:
        tree.column(c, width=200)

def add_word_popup():
    win = tk.Toplevel(root)
    win.title("Add new word")
    win.grab_set()

    #Center Window + Size ------
    win.update_idletasks()
    w = 380
    h = 180
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # set grid info
    win.grid_columnconfigure(0, weight=0)
    win.grid_columnconfigure(1, weight=1)
    win.grid_rowconfigure(0, weight=1)
    win.grid_rowconfigure(1, weight=1)
    win.grid_rowconfigure(2, weight=1)
    win.grid_rowconfigure(3, weight=0)
    
    # Inputs
    tk.Label(win, text="Word").grid(row=0, column=0, padx=8, pady=6)
    e_word = tk.Entry(win, width=40, font=livvic_font)
    e_word.grid(row=0, column=1, padx=8, pady=6, sticky="nsew")

    tk.Label(win, text="Meaning").grid(row=1, column=0, padx=8, pady=6)
    e_mean = tk.Entry(win, width=40, font=livvic_font)
    e_mean.grid(row=1, column=1, padx=8, pady=6, sticky="nsew")

    tk.Label(win, text="Example").grid(row=2, column=0, padx=8, pady=6)
    e_ex = tk.Entry(win, width=40, font=livvic_font)
    e_ex.grid(row=2, column=1, padx=8, pady=6, sticky="nsew")

    # OK handler
    def on_ok():
        w = e_word.get().strip()
        m = e_mean.get().strip()
        ex = e_ex.get().strip()

        if not w:
            messagebox.showwarning("Validation", "Word cannot be empty.")
            return

        tree.insert("", "end", values=(w, m, ex))
        win.destroy()

    # Button
    tk.Button(win, text="Add", command=on_ok, bg=ACCENT, fg="white")\
        .grid(row=3, column=0, columnspan=2, pady=8)

    # Auto focus + Enter = Add
    e_word.focus_set()
    win.bind("<Return>", lambda event: on_ok())

    win.wait_window()


def delete_selected_word():
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Select", "Please select a row to delete.")
        return
    tree.delete(sel[0])

def save_table_to_file():
    all_vals = []
    for item in tree.get_children():
        w, m, ex = tree.item(item, "values")
        all_vals.append({"word": w, "meaning": m, "example": ex})
    ok = save_vocab(all_vals)
    if ok:
        messagebox.showinfo("Saved", f"Saved {len(all_vals)} words to {VOCAB_FILE}")
    else:
        messagebox.showerror("Error", "Failed to save vocab file.")

def load_table_from_file():
    refresh_vocab_table()
    messagebox.showinfo("Loaded", f"Loaded from {VOCAB_FILE}")

tk.Button(btns_frame, text="Add", command=add_word_popup, bg=BTN_GREEN, fg="white").grid(row=0, column=0, sticky="ew", padx=6)
tk.Button(btns_frame, text="Delete", command=delete_selected_word, bg="#e74c3c", fg="white").grid(row=0, column=1, sticky="ew", padx=6)
tk.Button(btns_frame, text="Save", command=save_table_to_file, bg=ACCENT, fg="white").grid(row=0, column=2, sticky="ew", padx=6)
tk.Button(btns_frame, text="Refresh", command=refresh_vocab_table, bg="#95a5a6", fg="white").grid(row=0, column=3, sticky="ew", padx=6)

def practice_vocab_with_ai():
    # Read vocab.json and call AI to generate practice quiz, show in chat
    data = load_vocab() # retun json.load(f) if ok
    if not data:
        messagebox.showinfo("No vocab", "Vocabulary list is empty. Add words first.")
        return
    words = [item["word"] for item in data]
    word_list_str = ", ".join(words)

    prompt = (
    f"Write a short, natural, coherent, meaningful and logical paragraph, B2 level, "
    f"containing all of the words below. No explanation, no listing.\n"
    f"Words: {word_list_str}"
)

    append_ai_message_to_chat("Creating vocabulary passage include all words in vocab...")

    def worker(p):
        try:
            if client is None:
                raise RuntimeError("OpenAI client not configured (OPENAI_API_KEY missing).")
            resp = client.responses.create(
                model="gpt-4.1-nano",
                input=[{"role":"user","content": p}],
                max_output_tokens=1000
            )
            out = resp.output_text if hasattr(resp, "output_text") else None
            if not out:
                # try fallback to older shape
                try:
                    out = resp.output[0].content[0].text
                except Exception:
                    out = str(resp)
        except Exception as e:
            out = f"Error generating practice: {e}"
        root.after(0, append_ai_message_to_chat, out)

    threading.Thread(target=worker, args=(prompt,), daemon=True).start()

tk.Button(btns_frame, text="🧠 Practice", command=practice_vocab_with_ai, bg="#8e44ad", fg="white").grid(row=0, column=4, sticky="ew", padx=6)

# initial load
if not os.path.exists(VOCAB_FILE):
    # create a sample
    sample = [
        {"word":"apple","meaning":"quả táo","example":"I eat an apple every day."},
        {"word":"run","meaning":"chạy","example":"He runs fast."}
    ]
    save_vocab(sample)
refresh_vocab_table()


right_frame = tk.Frame(root, bg=TITLE_BG)
right_frame.grid(row=0, column=1, sticky="nsew", padx=(10,20), pady=20)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=0)
right_frame.grid_rowconfigure(2, weight=0)
right_frame.grid_columnconfigure(0, weight=1)

chat_card = tk.Frame(right_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
chat_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0,8))
chat_card.grid_rowconfigure(0, weight=1)
chat_card.grid_columnconfigure(0, weight=1)

chat_area = scrolledtext.ScrolledText(chat_card, wrap=tk.WORD, font=livvic_font, bg=TEXT_BG, padx=10, pady=10, state=tk.NORMAL)
chat_area.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)

chat_area.tag_configure("user", foreground="#ffffff", background="#2c3e50", lmargin1=40, lmargin2=40, rmargin=10, spacing3=8, justify="right")
chat_area.tag_configure("ai", foreground="#2c3e50", background="#e9f6ff", lmargin1=10, lmargin2=10, rmargin=40, spacing3=8, justify="left")
chat_area.tag_configure("meta", foreground="#7f8c8d", font=("Arial", 9), justify="center")

def append_user_message_to_chat(msg):
    if not msg.strip():
        return
    chat_area.insert(tk.END, "" + msg + "\n", "user")
    chat_area.see(tk.END)

def append_ai_message_to_chat(msg):
    chat_area.insert(tk.END, "" + msg + "\n", "ai")
    chat_area.see(tk.END)

# input area
ai_input_frame = tk.Frame(right_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
ai_input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(8,0))
ai_input_frame.grid_columnconfigure(0, weight=1)
# ai_input_frame.grid_columnconfigure(1, weight=0)
ai_input_frame.grid_rowconfigure(0, weight=1)

ai_input_textarea = scrolledtext.ScrolledText(ai_input_frame, wrap=tk.WORD, height=5, font=livvic_font, bg=TEXT_BG, relief="flat", padx=10, pady=10)
ai_input_textarea.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

# send to AI
def send_to_ai_from_input():
    user_msg = ai_input_textarea.get(1.0, tk.END).strip()
    if not user_msg:
        return
    ai_input_textarea.delete(1.0, tk.END)
    append_user_message_to_chat(user_msg)

    def worker(text):
        try:
            if client is None:
                raise RuntimeError("OpenAI client not configured (OPENAI_API_KEY missing).")
            resp = client.responses.create(
                model="gpt-4.1-nano",
                input=[{"role":"user","content": text}],
                max_output_tokens=300
            )
            out = getattr(resp, "output_text", None)
            if not out:
                try:
                    out = resp.output[0].content[0].text
                except Exception:
                    out = str(resp)
        except Exception as e:
            out = f"Error: {e}"
        root.after(0, append_ai_message_to_chat, out)
        try:
            read_text(out)
        except Exception:
            pass

    threading.Thread(target=worker, args=(user_msg,), daemon=True).start()

# Record answer (text flow): record and convert to text then send
def record_ai_and_send_text(btn_widget):
    toggle_record_for_area("en", ai_input_textarea, btn_widget)
    if not globals().get("recording", False):
        user_msg = ai_input_textarea.get(1.0, tk.END).strip()
        if user_msg:
            root.after(150, send_to_ai_from_input)

# Record answer (audio file) and optionally send to audio-model (not used for practice)
def record_ai_and_save_audio_and_send_for_eval(btn_widget):
    global recording, recorded_frames, stream
    filename = os.path.join(RECORDINGS_DIR, f"user_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
    if not recording:
        recorded_frames = []
        def callback(indata, frames, time, status):
            if recording:
                recorded_frames.append(indata.copy())
        stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback)
        stream.start()
        recording = True
        btn_widget.config(text="Stop Recording")
        ai_input_textarea.insert(tk.END, "\nRecording... Speak now.\n")
    else:
        recording = False
        if stream:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass
            stream = None
        if not recorded_frames:
            ai_input_textarea.insert(tk.END, "\nNo audio recorded.\n")
            btn_widget.config(text="Record Answer")
            return
        audio_data = np.concatenate(recorded_frames, axis=0)
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data.tobytes())
        ai_input_textarea.insert(tk.END, f"\nSaved: {filename}\n")
        btn_widget.config(text="🎙️ Record Answer")
        # If want to send audio to AI (audio model), implement here (requires quota & audio model)
        # For now I just save and show path.

# UI buttons on right
ai_btn_input_frame = tk.Frame(right_frame, bg=CARD_BG)
ai_btn_input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(8,0))
ai_btn_input_frame.grid_columnconfigure(0, weight=1)
ai_btn_input_frame.grid_columnconfigure(1, weight=1)
ai_btn_input_frame.grid_rowconfigure(0, weight=1)

record_button_answer = tk.Button(ai_btn_input_frame, text="Record Answer", font=livvic_font, bg=BTN_GREEN, fg="white", relief="flat",
                                 width=14, command=lambda: record_ai_and_send_text(record_button_answer))
record_button_answer.grid(row=0, column=0, padx=(6,12), pady=12, sticky="ew")

send_btn = tk.Button(ai_btn_input_frame, text="Send to AI", font=livvic_font, bg=ACCENT, fg="white", relief="flat",
                     width=12, command=send_to_ai_from_input)
send_btn.grid(row=0, column=1, padx=6, pady=12, sticky="ew")

append_ai_message_to_chat("Hi! I'm an English tutor. Ask me anything.")

root.mainloop()
