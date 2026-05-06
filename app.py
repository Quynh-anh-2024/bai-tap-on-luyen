from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Tải API Key từ file .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình Gemini API
genai.configure(api_key=API_KEY)

# Khởi tạo app Flask và cho phép Frontend gọi API
app = Flask(__name__)
CORS(app) 

# Cấu hình System Prompt (áp dụng strict rules và MathJax như đã bàn)
SYSTEM_INSTRUCTION = """
Bạn là chuyên gia thiết kế đề thi tiểu học.
Hãy xuất MẢNG JSON gồm các câu hỏi.
Tuyệt đối không dùng dấu gạch chéo cho phân số, bắt buộc dùng chuẩn LaTeX \(\frac{tử}{mẫu}\).
... (Dán toàn bộ phần System Prompt ở câu trả lời trước vào đây) ...
"""

# Khai báo model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Dùng bản flash cho tốc độ nhanh và chi phí rẻ
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={"response_mime_type": "application/json"} # Ép trả về chuẩn JSON
)

# Tạo đường dẫn API (Endpoint) để Frontend gọi vào
@app.route('/api/sinh-de', methods=['POST'])
def sinh_de_thi():
    try:
        # Lấy dữ liệu người dùng gửi lên từ web
        data = request.json
        mon_hoc = data.get('subject')
        khoi_lop = data.get('grade')
        chu_de = data.get('topic')
        sl_nhan_biet = data.get('nb')
        sl_thong_hieu = data.get('th')
        sl_van_dung = data.get('vd')

        # Gom lại thành câu lệnh Prompt
        user_prompt = f"Tạo đề môn {mon_hoc} lớp {khoi_lop}, chủ đề: {chu_de}. Tỉ lệ: Nhận biết {sl_nhan_biet} câu, Thông hiểu {sl_thong_hieu} câu, Vận dụng {sl_van_dung} câu."

        # Gọi Gemini
        response = model.generate_content(user_prompt)
        
        # Trả cục JSON của Gemini thẳng về cho Frontend
        return response.text, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Chạy server ở cổng 5000
    app.run(debug=True, port=5000)