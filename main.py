import tkinter as tk
from tkinter import scrolledtext, font
import threading
import numpy as np
import pyttsx3
from deep_translator import GoogleTranslator
from openai import OpenAI
import os
import sounddevice as sd
import speech_recognition as sr
import wave
from datetime import datetime
import base64

recording = False
recorded_frames = []
stream = None

root = tk.Tk()
root.title("🎓 English Study Box")
root.config(bg="#f8f9fa")

# Fullscreen & exit with Esc
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# Fonts & basic styling
try:
    livvic_font = font.Font(family="Livvic", size=13)
except:
    livvic_font = font.Font(family="Arial", size=13)

TITLE_BG = "#f8f9fa"
CARD_BG = "#ffffff"
ACCENT = "#3498db"
BTN_GREEN = "#2ecc71"
TEXT_BG = "#fafafa"

# Use grid: 2 columns (left/right) each 50%
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)


# --------------------------
# LEFT COLUMN (3 stacked blocks)
# --------------------------
left_frame = tk.Frame(root, bg=TITLE_BG)
left_frame.grid(row=0, column=0, sticky="nsew", padx=(20,10), pady=20)
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=1)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

# header = tk.Label(left_frame, text="ENGLISH STUDY BOX — INPUTS", font=("Livvic", 18, "bold"), bg=TITLE_BG, fg="#2c3e50")
# header.grid(row= 0, column=0, sticky="w", padx=5, pady=(0,10))  # decorative header

def make_io_block(parent, title, lang_code_label, record_lang, translate_from, translate_to, read_source_area_target):
    """
    Create a block with left button column and right text area.
    - record_lang: "vn" or "en" (for toggleRecording)
    - translate_from/translate_to: codes for translate()
    - read_source_area_target: which text area to read for 'Read' button (Text widget)
    """
    block = tk.Frame(parent, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
    block.grid_columnconfigure(0, weight=0)
    block.grid_columnconfigure(1, weight=1)
    block.grid_rowconfigure(0, weight=1)

    header = tk.Label(block, text=title, font=("Livvic", 14, "bold"), bg=CARD_BG, fg="#2c3e50")
    header.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10,0))

    btn_col = tk.Frame(block, bg=CARD_BG)
    btn_col.grid(row=1, column=0, sticky="ns", padx=10, pady=10)

    text_area = scrolledtext.ScrolledText(
        block,
        wrap=tk.WORD,
        font=livvic_font,
        bg=TEXT_BG,
        relief="flat",
        highlightbackground="#dcdde1",
        highlightthickness=1,
        padx=10, pady=10
    )
    text_area.grid(row=1, column=1, sticky="nsew", padx=(0,12), pady=10)

    # Buttons
    record_btn = tk.Button(btn_col, text="🎙️ Record", font=livvic_font, bg=BTN_GREEN, fg="white", width=18, relief="flat")
    record_btn.pack(pady=6)

    translate_btn = tk.Button(btn_col, text="🌐 Translate", font=livvic_font, bg=ACCENT, fg="white", width=18, relief="flat")
    translate_btn.pack(pady=6)

    read_btn = tk.Button(btn_col, text="🔊 Read", font=livvic_font, bg=ACCENT, fg="white", width=18, relief="flat")
    read_btn.pack(pady=6)

    # map commands (use closures)
    record_btn.config(command=lambda: toggleRecording(record_lang, text_area, record_btn))
    # translate: translate text from this text_area and put into the other side (for VN block -> EN block, etc.)
    # We'll accept translate_from/translate_to strings like "vn" / "en" mapped to "vi"/"en" for translator
    def translate_cmd():
        src = text_area.get(1.0, tk.END).strip()
        if not src:
            text_area.insert(tk.END, "\n⚠️ Nothing to translate.")
            return
        # map simple codes
        translate_from
        translate_to
        try:
            translated = translate(translate_from, translate_to, src)
            # place result into the paired target area depending on arguments
            # read_source_area_target param will be a callable that returns the target area
            target_area = read_source_area_target()
            target_area.delete(1.0, tk.END)
            target_area.insert(tk.END, translated)
        except Exception as e:
            text_area.insert(tk.END, f"\n❌ Translate error: {e}")

    translate_btn.config(command=translate_cmd)
    read_btn.config(command=lambda: readInput(read_source_area_target()))

    return block, text_area, record_btn, translate_btn, read_btn

# We'll create placeholders for blocks and then we can reference sibling areas for translations
vn_block_frame, vn_text_area, vn_rec_btn, vn_trans_btn, vn_read_btn = make_io_block(left_frame, "🗣️ Vietnamese Input", "VN", "vi", "vi", "en", lambda: None)
en_block_frame, en_text_area, en_rec_btn, en_trans_btn, en_read_btn = make_io_block(left_frame, "🗣️ English Input", "EN", "en", "en", "vi", lambda: None)
trans_block = tk.Frame(left_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)

# place them
vn_block_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0,8))
en_block_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=8)
trans_block.grid(row=2, column=0, sticky="nsew", padx=5, pady=(8,0))

# Now fix the translate/read callbacks to point to the correct sibling areas
# For VN block: translate -> put into en_text_area; read button should read en_text_area
vn_trans_btn.config(command=lambda: getAndSetTranslatedText(vn_text_area, en_text_area, "vi", "en"))
vn_read_btn.config(command=lambda: readInput(en_text_area))

# For EN block: translate -> put into vn_text_area; read button read en_text_area
en_trans_btn.config(command=lambda: getAndSetTranslatedText(en_text_area, vn_text_area, "en", "vi"))
en_read_btn.config(command=lambda: readInput(en_text_area))

# --------------------------
# Translation Box (third block)
# --------------------------
trans_block.grid_columnconfigure(0, weight=1)
trans_block.grid_columnconfigure(1, weight=0)
trans_block.grid_columnconfigure(2, weight=1)
trans_block.grid_rowconfigure(0, weight=1)

left_trans_area = scrolledtext.ScrolledText(
    trans_block,
    wrap=tk.WORD,
    font=livvic_font,
    bg=TEXT_BG,
    relief="flat",
    padx=10, pady=10
)
left_trans_area.grid(row=0, column=0, sticky="nsew", padx=(12,6), pady=12)

mid_btns = tk.Frame(trans_block, bg=CARD_BG)
mid_btns.grid(row=0, column=1, sticky="nsew", padx=6, pady=12)

right_trans_area = scrolledtext.ScrolledText(
    trans_block,
    wrap=tk.WORD,
    font=livvic_font,
    bg=TEXT_BG,
    relief="flat",
    padx=10, pady=10
)
right_trans_area.grid(row=0, column=2, sticky="nsew", padx=(6,12), pady=12)
def translate(from_lang, to_lang, input_text):
    translated = GoogleTranslator(source=from_lang, target=to_lang).translate(input_text)
    return translated

def getAndSetTranslatedText(get_area, set_area, from_lang, to_lang):
    user_input = get_area.get(1.0, tk.END).strip()
    trans_text = translate(from_lang, to_lang, user_input)
    set_area.insert(tk.END, "\n\n" + trans_text)

def toggleRecording(language, text_area, btn_widget=None):
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
                btn_widget.config(text="⏹ Stop Recording")
        except Exception as e:
            recording = False
            if btn_widget:
                btn_widget.config(text="🎙️ Start Recording")
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
            text_area.insert(tk.END, "\n⚠️ No audio recorded.")
            if btn_widget:
                btn_widget.config(text="🎙️ Start Recording")
            return

        try:
            audio_data = np.concatenate(recorded_frames, axis=0)
            audio_bytes = audio_data.tobytes()
            sample_width = audio_data.dtype.itemsize  # thường 2 cho int16
            audio = sr.AudioData(audio_bytes, 16000, sample_width)

            recognizer = sr.Recognizer()
            recognized_text = recognizer.recognize_google(audio, language=lang_code)

            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, recognized_text)

        except sr.UnknownValueError:
            text_area.insert(tk.END, "\n⚠️ Could not understand the audio.")
        except sr.RequestError as e:
            text_area.insert(tk.END, f"\n❌ Speech recognition error: {e}")
        except Exception as e:
            text_area.insert(tk.END, f"\n⚠️ Error: {e}")

        if btn_widget:
            btn_widget.config(text="🎙️ Start Recording")

def readInput(text_area):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id if len(voices) > 1 else voices[0].id)
    user_input = text_area.get(1.0, tk.END).strip()
    if user_input:
        engine.say(user_input)
        engine.runAndWait()
    engine.stop()

def readText(text):
    mouth = pyttsx3.init()
    mouth.say(text)
    mouth.runAndWait()
    mouth.stop()
    
def ai_thinking(request):
    print("request:", request)
    try:
        client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": "Cô giáo Tiếng Anh, trả lời súc tích."},
                {"role": "user", "content": request},
            ],
            max_output_tokens=100,
            temperature=0.7, # độ sáng tạo 0: nghiêm ngặt, 1: sáng tạo
        )
        print("response: " + response.output[0].content[0].text)
        return response.output[0].content[0].text
    except:
        return "Hiện tại tôi đang gặp lỗi, vui lòng thử lại sau."
    
def do_translate_left_to_right():
    getAndSetTranslatedText(left_trans_area, right_trans_area, "vi", "en")
def do_translate_right_to_left():
    getAndSetTranslatedText(right_trans_area, left_trans_area, "en", "vi")
def do_read_right():
    readInput(right_trans_area)

tk.Button(mid_btns, text="VN ⮕ EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat", command=do_translate_left_to_right).pack(pady=6)
tk.Button(mid_btns, text="VN ⭠ EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat", command=do_translate_right_to_left).pack(pady=6)
tk.Button(mid_btns, text="Read EN", font=livvic_font, bg=ACCENT, fg="white", width=12, relief="flat", command=do_read_right).pack(pady=6)

# --------------------------
# RIGHT COLUMN (AI chat)
# --------------------------
right_frame = tk.Frame(root, bg=TITLE_BG)
right_frame.grid(row=0, column=1, sticky="nsew", padx=(10,20), pady=20)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=0)
right_frame.grid_columnconfigure(0, weight=1)

chat_card = tk.Frame(right_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
chat_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0,8))
chat_card.grid_rowconfigure(0, weight=1)
chat_card.grid_columnconfigure(0, weight=1)

# chat_label = tk.Label(chat_card, text="💬 Chat with AI", font=("Livvic", 14, "bold"), bg=CARD_BG, fg="#2c3e50")
# chat_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10,0))

chat_area = scrolledtext.ScrolledText(
    chat_card,
    wrap=tk.WORD,
    font=livvic_font,
    bg=TEXT_BG,
    relief="flat",
    padx=10, pady=10,
    state=tk.NORMAL
)
chat_area.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)

# tags for styling bubbles
chat_area.tag_configure("user", foreground="#ffffff", background="#2c3e50", lmargin1=40, lmargin2=40, rmargin=10, spacing3=8, justify="right")
chat_area.tag_configure("ai", foreground="#2c3e50", background="#e9f6ff", lmargin1=10, lmargin2=10, rmargin=40, spacing3=8, justify="left")
chat_area.tag_configure("meta", foreground="#7f8c8d", font=("Arial", 9), justify="center")

# input area (for user to review or type before sending)
ai_input_frame = tk.Frame(right_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
ai_input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(8,0))
ai_input_frame.grid_columnconfigure(0, weight=1)
ai_input_frame.grid_columnconfigure(1, weight=0)
# ai_input_frame.grid_columnconfigure(2, weight=0)

ai_input_textarea = scrolledtext.ScrolledText(ai_input_frame, wrap=tk.WORD, height=5, font=livvic_font, bg=TEXT_BG, relief="flat", padx=10, pady=10)
ai_input_textarea.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

# Send and Record buttons for AI
def append_user_message_to_chat(msg):
    if not msg.strip():
        return
    chat_area.insert(tk.END, "" + msg + "\n", "user")
    chat_area.see(tk.END)

def append_ai_message_to_chat(msg):
    chat_area.insert(tk.END, "" + msg + "\n", "ai")
    chat_area.see(tk.END)

def send_to_ai_from_input():
    user_msg = ai_input_textarea.get(1.0, tk.END).strip()
    if not user_msg:
        return
    ai_input_textarea.delete(1.0, tk.END)
    append_user_message_to_chat(user_msg)

    # run AI call in background
    def worker(text):
        try:
            reply = ai_thinking(text)
        except Exception as e:
            reply = f"Error: {e}"
        # show AI reply in main thread
        # readText(reply)
        root.after(0, append_ai_message_to_chat, reply)
        # read AI reply
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            voices = engine.getProperty("voices")
            engine.setProperty("voice", voices[1].id if len(voices) > 1 else voices[0].id)
            engine.say(reply)
            engine.runAndWait()
            engine.stop()
        except Exception:
            pass

    threading.Thread(target=worker, args=(user_msg,), daemon=True).start()

def record_ai_and_send_text(btn_widget):
    # Gọi hàm toggleRecording đã có; nhấn nút sẽ chuyển đổi trạng thái bắt đầu/dừng (ghi âm).
    # Sau khi hàm toggleRecording trả về, nếu trạng thái ghi âm là False (Đã dừng) thì âm thanh đã được xử lý xong.
    # Và văn bản đã được chèn vào ô nhập liệu. Vì thế, chúng ta sẽ tự động gửi nó đi.
    toggleRecording("en", ai_input_textarea, btn_widget)
    # nếu chúng ta vừa dừng lại (ghi False) và có văn bản -> gửi
    if not globals().get("recording", False):
        user_msg = ai_input_textarea.get(1.0, tk.END).strip()
        if user_msg:
            # delay nhỏ để cập nhật ui
            root.after(100, send_to_ai_from_input)

def record_ai_and_send_audio(btn_widget):
    """Hàm ghi âm giọng nói để AI chấm phát âm"""
    global recording, recorded_frames, stream

    recordings_dir = "recordings"
    os.makedirs(recordings_dir, exist_ok=True)
    filename = os.path.join(recordings_dir, f"user_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

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
            ai_input_textarea.insert(tk.END, "\n⚠️ No audio recorded.\n")
            btn_widget.config(text="Record Answer")
            return

        audio_data = np.concatenate(recorded_frames, axis=0)

        # Lưu file .wav
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)
            wf.writeframes(audio_data.tobytes())

        ai_input_textarea.insert(tk.END, f"\nSaved: {filename}\n")
        btn_widget.config(text="Record Answer")

        # Gửi cho AI để đánh giá phát âm
        root.after(200, lambda: evaluate_pronunciation(filename))

def evaluate_pronunciation(audio_path):
    """Gửi file âm thanh tới AI để chấm phát âm"""
    ai_input_textarea.insert(tk.END, "\n🤖 Sending audio to AI for evaluation...\n")
    ai_input_textarea.see(tk.END)
    root.update_idletasks()

    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        # --- Đọc và encode audio thành base64 ---
        with open(audio_path, "rb") as f:
            wav_data = f.read()
        encoded_string = base64.b64encode(wav_data).decode("utf-8")

        # --- Gửi lên API ---
        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "alloy", "format": "wav"},
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là giáo viên tiếng Anh, hãy nghe đoạn ghi âm của học viên "
                               "và chấm điểm phát âm, chỉ ra lỗi, đưa gợi ý cải thiện."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Xin hãy đánh giá phát âm của tôi trong đoạn ghi âm sau."
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded_string,
                                "format": "wav"
                            }
                        }
                    ]
                }
            ]
        )

        feedback = completion.choices[0].message["content"][0]["text"]
        ai_input_textarea.insert(tk.END, f"\n🎧 AI Feedback:\n{feedback}\n")
        ai_input_textarea.see(tk.END)

    except Exception as e:
        ai_input_textarea.insert(tk.END, f"\n❌ Error sending audio: {e}\n")
        ai_input_textarea.see(tk.END)



ai_btn_input_frame = tk.Frame(ai_input_frame, bg=CARD_BG, highlightbackground="#dfe6e9", highlightthickness=1)
ai_btn_input_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=(8,0))
ai_btn_input_frame.grid_rowconfigure(0, weight=0)
ai_btn_input_frame.grid_rowconfigure(1, weight=0)
ai_btn_input_frame.grid_columnconfigure(0, weight=1)

record_button_answer = tk.Button(ai_btn_input_frame, text="Record Answer", font=livvic_font, bg=BTN_GREEN, fg="white", relief="flat", width=14, command=lambda: record_ai_and_send_text(record_button_answer))
record_button_answer.grid(row=1, column=0, padx=(6,12), pady=12, sticky="ew")

send_btn = tk.Button(ai_btn_input_frame, text="Send to AI", font=livvic_font, bg=ACCENT, fg="white", relief="flat", width=12, command=send_to_ai_from_input)
send_btn.grid(row=0, column=0, padx=6, pady=12, sticky="ew")

append_ai_message_to_chat("Xin chào! Tôi là trợ lý học tiếng Anh. Hãy hỏi tôi bất cứ điều gì.")

root.mainloop()
