#ứng dụng AI giao tiếp với con người
import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import os
from gtts import gTTS

def noi_tieng_anh(english_text):
    mouth = pyttsx3.init()
    mouth.say(english_text)
    mouth.runAndWait()
    
def noi_tieng_viet(english_text):
    tts = gTTS(text=english_text, lang='vi')
    tts.save("voice.mp3")
    
def nghe(language):
    ear = sr.Recognizer()
    lang_code = "vi-VN" if language == "vietnamese" else "en-US"
    with sr.Microphone() as mic:
        print("AI: Tôi đang lắng nghe bạn nói...")
        audio = ear.listen(mic)
    try:
        listened_text = ear.recognize_google(audio, language=lang_code)
    except:
        listened_text = ""
    return listened_text
    
def suy_nghi(request):
    try:
        client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": "bạn là giáo viên cấp hai, trả lời ngắn gọn xúc tích"},
                {"role": "user", "content": request},
            ],
            max_output_tokens=100,
            # temperature=0.7, # độ sáng tạo 0: nghiêm ngặt, 1: sáng tạo
        )
        return response.output_text
    except:
        return "Hiện tại tôi đang gặp lỗi, vui lòng thử lại sau."

def ai_thinking(request):
    try:
        client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
        print("key", os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": "Cô giáo Tiếng Anh, trả lời súc tích."},
                {"role": "user", "content": request},
            ],
            max_output_tokens=100,
            temperature=0.7, # độ sáng tạo 0: nghiêm ngặt, 1: sáng tạo
        )
        print(response.output[0].content[0].text)
        print(response)
        return response.output[0].content[0].text
    except:
        return "Hiện tại tôi đang gặp lỗi, vui lòng thử lại sau."
    
ai_thinking("Hello, how are you?")