# 🎓 English Study Box
### Ứng dụng học tiếng Anh toàn diện dành cho người Việt

---

## 📘 Giới thiệu

**English Study Box** là một ứng dụng học tiếng Anh thông minh, thân thiện và trực quan.  
Dự án kết hợp sức mạnh của **AI (OpenAI GPT)**, **Speech Recognition**, **Text-to-Speech**, và **dịch thuật tự động** để tạo ra môi trường học tập hiệu quả — giúp người học:
- Luyện **phát âm tiếng Anh** qua ghi âm và phản hồi.
- Dịch qua lại **Anh ↔ Việt** dễ dàng.
- **Lưu và quản lý từ vựng** cá nhân bằng bảng chỉnh sửa trực tiếp.
- Tương tác **trò chuyện với AI giáo viên tiếng Anh**.
- Tự động sinh **bài tập luyện từ vựng** dựa trên dữ liệu của người học.

---

## 👨‍🏫 Đối tượng sử dụng

Ứng dụng phù hợp cho:
- **Sinh viên, học sinh** đang học tiếng Anh ở mọi trình độ.
- **Người đi làm** muốn cải thiện khả năng giao tiếp và phản xạ ngôn ngữ.
- **Người học tự do** cần công cụ học tập có trợ lý AI và khả năng tương tác trực tiếp bằng giọng nói.

---

## 🌟 Tính năng nổi bật

### 🗣 Translation Box
- Hai ô song song (tiếng Việt ↔ tiếng Anh).
- Dịch tự động, đọc to văn bản, và ghi âm giọng nói để nhận diện.
- Giao diện trực quan, dễ thao tác.

### 📚 Vocabulary Box
- Quản lý từ vựng qua bảng:
  - Cột: **Word**, **Meaning**, **Example**
  - Hỗ trợ **chỉnh sửa trực tiếp** bằng double-click hoặc popup thêm mới.
- Các nút chức năng:
  - ➕ Add — thêm từ mới
  - 🗑 Delete — xóa dòng chọn
  - 💾 Save — lưu dữ liệu vào `vocab.json`
  - 🔁 Refresh — tải lại từ file
  - 🧠 Practice — gửi danh sách từ cho AI sinh **bài tập trắc nghiệm**

### 🤖 AI Chat Box
- Trò chuyện tự nhiên hai chiều với AI giáo viên.
- AI hiểu ngữ cảnh, hỗ trợ luyện tập, sửa lỗi ngữ pháp, đặt câu, giải thích ngữ pháp, v.v.
- Có thể **ghi âm giọng nói** hoặc **gửi text**.
- Khi luyện từ vựng, AI sẽ tạo **quiz và phản hồi ngay trong cửa sổ chat**.

### 🎙 Audio System
- Ghi âm tự động lưu tại thư mục `recordings/` với tên dạng: recordings/user_audio_YYYYMMDD_HHMMSS.wav
- Nhận diện giọng nói tiếng Việt và tiếng Anh bằng Google Speech API.
- Đọc văn bản bằng TTS (`pyttsx3`).

---

## ⚙️ Cài đặt & Sử dụng

- Các bạn muốn dùng dự án vui lòng truy cập https://platform.openai.com/settings/organization/api-keys để tạo api key 
- Sau đó tạo biến môi trường để lưu key:
    Có thể lưu thủ công bằng mở window -> search "enviroment variable" -> click "new" -> nhập "OPENAI_API_KEY" -> click "add" -> nhập key -> click "ok"
    Cách khác là mở terminal, nhập "setx OPENAI_API_KEY '[key]'". Sau đó kiểm tra bằng lệnh "echo %OPENAI_API_KEY%" để xem key vừa nhập đúng chưa


### 1️⃣ Cài đặt thư viện
Chạy lệnh trong Terminal:
```bash
    pip install -r requirements.txt to install dependencies for main.py

    python main.py to run main.py
```

---

### 💡 Mẹo sử dụng hiệu quả

- 🗣 Ghi âm – Dịch – Nghe lại: rèn phát âm và phản xạ.

- 📖 Lưu từ vựng mỗi ngày, dùng nút Practice để ôn.

- 💬 Trò chuyện với AI về các chủ đề hàng ngày.

- 🧠 Nhờ AI tạo quiz hoặc viết đoạn văn sử dụng các từ vựng của bạn.

### Tác giả
- Lại Trọng Minh Trường - [Github](https://github.com/LaiTrongMinhTruong)

### 📝 Dự án mã nguồn mở, phi thương mại.
### Tự do chỉnh sửa, cải tiến và sử dụng cho mục đích học tập cá nhân.