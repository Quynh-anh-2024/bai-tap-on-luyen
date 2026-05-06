from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

app = Flask(__name__)
CORS(app) 

# Thầy tự dán lại đoạn System Prompt dài dòng của thầy vào giữa 3 dấu ngoặc kép này nhé
SYSTEM_INSTRUCTION = r"""
Bạn là chuyên gia thiết kế đề thi tiểu học xuất sắc theo chương trình Giáo dục Phổ thông 2018...
(Giữ nguyên nội dung Prompt cũ)
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={"response_mime_type": "application/json"} 
)

# ---- CHỨC NĂNG MỚI: PHỤC VỤ GIAO DIỆN WEB ----
@app.route('/')
def home():
    # Khi truy cập link chính, nó sẽ tự động gửi file index.html cho người dùng
    return send_from_directory('.', 'index.html')

# ---- CHỨC NĂNG CŨ: XỬ LÝ AI ----
@app.route('/api/sinh-de', methods=['POST'])
def sinh_de_thi():
    try:
        data = request.json
        mon_hoc = data.get('subject')
        khoi_lop = data.get('grade')
        chu_de = data.get('topic')
        sl_nhan_biet = data.get('nb')
        sl_thong_hieu = data.get('th')
        sl_van_dung = data.get('vd')

        user_prompt = f"Tạo đề môn {mon_hoc} lớp {khoi_lop}, chủ đề: {chu_de}. Tỉ lệ: Nhận biết {sl_nhan_biet} câu, Thông hiểu {sl_thong_hieu} câu, Vận dụng {sl_van_dung} câu."

        response = model.generate_content(user_prompt)
        return response.text, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)