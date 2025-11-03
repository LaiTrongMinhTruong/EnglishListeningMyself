import tkinter as tk
from tkinter import scrolledtext, font
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator

import sounddevice as sd
import numpy as np

def readInput():
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("voice", engine.getProperty("voices")[1].id)

    user_input = text_area.get(1.0, tk.END).strip()
    if user_input:
        engine.say(user_input)
        engine.runAndWait()
    engine.stop()
            
def translateText():
    user_input = text_area.get(1.0, tk.END).strip()
    if user_input:
        try:
            translated = GoogleTranslator(source='en', target='vi').translate(user_input)
            # text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "\n\n\n" + translated)
        except Exception as e:
            text_area.insert(tk.END, f"\n\nError during translation: {e}")

recording = False
recorded_frames = []
stream = None

def toggleRecording():
    global recording, recorded_frames, stream

    if not recording:
        # Bắt đầu ghi
        recording = True
        recorded_frames = []

        def callback(indata, frames, time, status):
            if recording:
                recorded_frames.append(indata.copy())

        stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback)
        stream.start()
        text_area.insert(tk.END, "\nRecording started... Speak now!")
        record_btn.config(text="⏹ Stop Recording")
    else:
        # Dừng ghi
        recording = False
        if stream:
            stream.stop()
            stream.close()

        text_area.insert(tk.END, "\nRecording stopped. Processing...")

        try:
            # Ghép tất cả frame lại
            audio_data = np.concatenate(recorded_frames, axis=0)
            audio_bytes = audio_data.tobytes()

            # Tạo AudioData cho speech_recognition
            audio = sr.AudioData(audio_bytes, 16000, 2)

            recognizer = sr.Recognizer()
            recognized_text = recognizer.recognize_google(audio)

            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, recognized_text)

        except sr.UnknownValueError:
            text_area.insert(tk.END, "\nCould not understand the audio.")
        except sr.RequestError as e:
            text_area.insert(tk.END, f"\nError with the speech recognition service: {e}")
        except Exception as e:
            text_area.insert(tk.END, f"\nAn error occurred: {e}")

        record_btn.config(text="🎙️ Start Recording")

# Khởi tạo cửa sổ tkinter
root = tk.Tk()
root.title("English Translate Box")
root.geometry("800x800")

try:
    livvic_font = font.Font(family="Livvic", size=14)
except:
    livvic_font = font.Font(family="Arial", size=14)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=livvic_font)
text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=10)

read_btn = tk.Button(button_frame, text="🔊 Read Article", command=readInput, font=livvic_font)
read_btn.pack(side=tk.LEFT, padx=5)

translate_btn = tk.Button(button_frame, text="🌐 Translate to Vietnamese", command=translateText, font=livvic_font)
translate_btn.pack(side=tk.LEFT, padx=5)

record_btn = tk.Button(button_frame, text="🎙️ Start Recording", command=toggleRecording, font=livvic_font)
record_btn.pack(side=tk.LEFT, padx=5)

root.mainloop()