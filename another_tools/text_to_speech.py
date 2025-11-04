import tkinter as tk
from tkinter import scrolledtext, font
import pyttsx3

#create a simple text input reader, input is from a text area shown in a tkinter window
def readInput():
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("voice", engine.getProperty("voices")[1].id)

    user_input = text_area.get(1.0, tk.END).strip()
    if user_input:
        engine.say(user_input)
        engine.runAndWait()
    engine.stop()

#initialize the tkinter window
root = tk.Tk()
root.title("English Input Reader")
root.geometry("800x800")

try:
    livvic_font = font.Font(family="Livvic", size=14)
except:
    livvic_font = font.Font(family="Arial", size=14)
    
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=livvic_font)
text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=10)

read_btn = tk.Button(button_frame, text="🔊 Read Article", command=readInput)
read_btn.pack(side=tk.LEFT, padx=5)

root.mainloop()
