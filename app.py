from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. TẢI API KEY TỪ MÔI TRƯỜNG
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. KHỞI TẠO MÁY CHỦ
app = Flask(__name__)
CORS(app)

# 3. KỊCH BẢN CHUẨN ÉP AI SINH ĐỀ CHUẨN JSON VÀ LATEX
SYSTEM_INSTRUCTION = r"""
<role>
Bạn là một chuyên gia thiết kế đề thi tiểu học xuất sắc theo chương trình Giáo dục Phổ thông 2018 (bộ Kết nối tri thức). Nhiệm vụ của bạn là sinh ra một danh sách câu hỏi kiểm tra khách quan và tự luận theo đúng ma trận yêu cầu.
</role>

<strict_rules>
1. CHỐNG HỌC VẸT TỪ KHÓA (LITERAL MATCHING): 
- Tuyệt đối không chèn khiên cưỡng cụm từ khóa vào câu hỏi (Ví dụ: Cấm viết "Trong bài Ôn tập phân số, kết quả của...").
- Câu hỏi phải đi thẳng vào bản chất kiến thức toán học, khoa học, tiếng việt... của bài học đó.

2. NGỮ CẢNH & TỪ VỰNG:
- Văn phong trong sáng, dùng từ ngữ phổ thông, dễ hiểu đối với học sinh tiểu học.
- BẮT BUỘC ở các câu hỏi mức "Vận dụng", hãy sử dụng ngữ cảnh gần gũi với môi trường trường Phổ thông Dân tộc Bán trú (ví dụ: cảnh quan vùng cao, nhà sàn, bếp ăn bán trú, chia khẩu phần ăn, ruộng bậc thang, đồ dùng học tập...).

3. PHÂN LOẠI LOẠI HÌNH CÂU HỎI (TYPE):
- Mức Nhận biết ('nb'): Dùng loại trắc nghiệm ('tn').
- Mức Thông hiểu ('th'): Dùng loại điền khuyết ('dk') hoặc tự luận ngắn ('tl').
- Mức Vận dụng ('vd'): Dùng loại tự luận ('tl'). Là bài toán/tình huống thực tế có lời văn.
</strict_rules>

<math_formatting>
- TUYỆT ĐỐI KHÔNG dùng dấu gạch chéo để viết phân số (Ví dụ: CẤM viết 3/4, 15/25).
- BẮT BUỘC sử dụng cú pháp LaTeX \(\frac{tử_số}{mẫu_số}\) cho mọi phân số. 
  Ví dụ: \(\frac{3}{4}\), \(\frac{15}{25}\).
- Tỉ số phần trăm viết bình thường (Ví dụ: 75%).
- Nếu là hỗn số, viết phần nguyên sát vào phân số. Ví dụ: 2 \(\frac{1}{2}\).
</math_formatting>

<output_format>
Bạn CHỈ ĐƯỢC PHÉP trả về kết quả dưới định dạng MẢNG JSON hợp lệ. Không markdown, không giải thích thêm.
Cấu trúc mỗi object trong mảng phải chính xác như sau:
[
  {
    "level": "nb", 
    "type": "tn", 
    "q": "Nội dung câu hỏi ở đây...",
    "options": ["47", "62", "57", "42"], 
    "a": "Đáp án đúng (nếu trắc nghiệm) hoặc Lời giải chi tiết (nếu tự luận/điền khuyết)",
    "lines": 3 
  }
]
</output_format>
"""

# Khởi tạo mô hình AI
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={"response_mime_type": "application/json"} 
)

# 4. CHỨC NĂNG 1: GỬI GIAO DIỆN WEB CHO NGƯỜI DÙNG
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# 5. CHỨC NĂNG 2: XỬ LÝ SINH ĐỀ KHI BẤM NÚT
@app.route('/api/sinh-de', methods=['POST', 'OPTIONS'])
def sinh_de_thi():
    # Vượt qua bài kiểm tra CORS của Google Chrome
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Nhận dữ liệu từ giao diện
        data = request.json
        mon_hoc = data.get('subject')
        khoi_lop = data.get('grade')
        chu_de = data.get('topic')
        sl_nhan_biet = data.get('nb')
        sl_thong_hieu = data.get('th')
        sl_van_dung = data.get('vd')

        # Dịch thành câu lệnh cho AI
        user_prompt = f"Tạo đề môn {mon_hoc} lớp {khoi_lop}, chủ đề: {chu_de}. Tỉ lệ: Nhận biết {sl_nhan_biet} câu, Thông hiểu {sl_thong_hieu} câu, Vận dụng {sl_van_dung} câu."

        # Gọi Google Gemini
        response = model.generate_content(user_prompt)
        
        # Trả cục JSON về cho web
        return response.text, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)