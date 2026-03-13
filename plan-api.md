# API Endpoints Plan (Detailed RESTful CRUD)

Tài liệu này định nghĩa chi tiết các API dựa ĐÚNG theo các trường có trong file \db.md\, bổ sung đầy đủ các tác vụ thao tác dữ liệu (CRUD: Create, Read, Update, Delete).

> **🎯 QUAN TRỌNG VỀ DATABASE SCHEMA:**
> Bảng \question_options\ trong \db.md\ hiện tại KHÔNG CÓ trường để lưu đáp án đúng. Để hệ thống có thể tự chấm điểm bài trắc nghiệm (MCQ), bạn cần bổ sung cột \is_correct (boolean)\ vào bảng \question_options\. Trong Payload dưới đây, tôi sẽ mặc định thiết kế có trường này để FE truyền lên.

---

## 1. Dịch Vụ Tệp Tin (File Upload)
*Lưu ý: API này để FE upload ảnh câu hỏi/đáp án lên R2 trước, lấy URL đưa vào Payload tạo/chỉnh sửa DB.*

- \POST /api/upload/image\
  - **Mô tả:** Upload ảnh lên Cloudflare R2
  - **Auth:** Require Token
  - **Request Form-Data:** \ile: [binary image]\
  - **Response 200:** \{ "url": "https://pub-<id>.r2.dev/questions/img.jpg" }\

---

## 2. Quản Lý Khảo Sát (Survey Management CRUD)
*Dành cho Admin/Researcher quản lý (Auth: Bearer Token)*

- \GET /api/surveys\
  - **Mô tả:** Lấy danh sách survey do user hiện tại tạo (hoặc tất cả nếu là ADMIN)
  - **Response 200:**
    \\\json
    [
      { "id": "uuid", "name": "Semester 1", "token": "uuid", "created_by": "user-uuid", "start_time": "...", "end_time": "...", "status": "active", "created_at": "..." }
    ]
    \\\

- \POST /api/surveys\
  - **Mô tả:** Tạo mới bài khảo sát (id và token tự render, created_by tự lấy từ Auth Token).
  - **Payload:**
    \\\json
    {
      "name": "Semester 1 Quiz",
      "start_time": "2026-03-01T00:00:00Z",
      "end_time": "2026-04-01T00:00:00Z",
      "status": "pending"
    }
    \\\
  - **Response 201:** Trả về Object Survey chứa \id\ và \	oken\ public.

- \GET /api/surveys/{survey_id}\
  - **Mô tả:** Xem chi tiết survey (kèm list Questions -> Options/Config)
  - **Response 200:** Khớp với bảng \surveys\, kèm lồng thêm mảng \questions\.

- \PUT /api/surveys/{survey_id}\
  - **Mô tả:** Cập nhật thông tin cấu hình Survey.
  - **Payload:** Các field cần update (\
ame\, \start_time\, \end_time\, \status\).

- \DELETE /api/surveys/{survey_id}\
  - **Mô tả:** Xóa Survey. (Lưu ý: Database xử lý cascade hoặc code logic báo lỗi nếu đã có responses).

---

## 3. Quản Lý Câu Hỏi (Question Management CRUD)
*Dành cho Admin/Researcher (Auth: Bearer Token)*

- \GET /api/surveys/{survey_id}/questions\
  - **Mô tả:** Lấy danh sách câu hỏi của một Survey

- \POST /api/surveys/{survey_id}/questions\
  - **Mô tả:** Tạo một câu hỏi mới. Dựa vào \	ype\ để insert thêm vào bảng \question_options\ hoặc \question_config\ tương ứng.
  - **Payload (Question Type MCQ):**
    \\\json
    {
      "type": "mcq",
      "title": "Which drawing is correct?",
      "question_image": "https://r2.../q1.jpg",
      "order_index": 1,
      "options": [
        { "image_url": "https://r2.../opt1.jpg", "order_index": 1, "is_correct": true },
        { "image_url": "https://r2.../opt2.jpg", "order_index": 2, "is_correct": false }
      ]
    }
    \\\
  - **Payload (Question Type Arrow/Angle):**
    \\\json
    {
      "type": "arrow",
      "title": "Point to the stop sign",
      "question_image": "https://r2.../q2.jpg",
      "order_index": 2,
      "config": {
        "correct_angle": 120.5,
        "tolerance": 15.0,
        "standing_position": "car",
        "looking_direction": "traffic light"
      }
    }
    \\\

- \PUT /api/questions/{question_id}\
  - **Mô tả:** Cập nhật nội dung câu hỏi hiện tại. Cơ chế: Update lại record \questions\ và xóa/tạo lại (hoặc tracking update) các row ở \question_options\ / \question_config\ đính kèm.
  - **Payload:** Cấu trúc tương tự như \POST\.

- \DELETE /api/questions/{question_id}\
  - **Mô tả:** Xóa câu hỏi khỏi bài khảo sát.

---

## 4. Trải Nghiệm Khảo Sát (Public APIs)
*Public API - Học sinh sử dụng (Không cần token, sử dụng \survey.token\ làm khóa định danh)*

- \GET /api/public/surveys/{token}\
  - **Mô tả:** Lấy nội dung thi (Tương đương Page 10+ nhưng cho User). Cần **ẨN KÍN** \is_correct\ và \correct_angle\ (Bên Backend lúc trả JSON về không được select các field này).

- \POST /api/public/surveys/{token}/start\
  - **Mô tả:** Bắt đầu bài khảo sát. Hành động này sẽ insert record vào bảng \participants\ và khởi tạo record vào bảng \ttempts\.
  - **Payload:** 
    \\\json
    {
      "name": "Jiara Martins",
      "school": "Ambience Public School",
      "grade": "6",
      "dob": "2012-05-15T00:00:00Z"
    }
    \\\
  - **Response 201:** \participant_id\, \ttempt_id\, \start_time\ (để FE track việc Submit sau đó).

- \POST /api/public/attempts/{attempt_id}/answers\
  - **Mô tả:** Học sinh chọn đáp án và lưu lên hệ thống. Insert/Update vào bảng \nswers\.
  - **Payload:** (Bulk update)
    \\\json
    {
      "answers": [
        { "question_id": "uuid-mcq-1", "selected_option_id": "uuid-option-1", "user_angle": null },
        { "question_id": "uuid-arrow-2", "selected_option_id": null, "user_angle": 130.5 }
      ]
    }
    \\\

- \PUT /api/public/attempts/{attempt_id}/submit\
  - **Mô tả:** Hành động Nộp bài cuối cùng. Update \end_time\ của \ttempts\, backend xử lý khớp lệnh logic ở \question_config/options\ chấm điểm \score\ tổng và chuyển \status = completed\.

---

## 5. Kết Quả & Thống Kê (Analytics)
*Auth: Bearer Token (Researcher/Admin)*

- \GET /api/surveys/{survey_id}/results\
  - **Mô tả:** Đọc bảng \ttempts\ tham chiếu với \participants\ (hiển thị giao diện Table danh sách).
  - **Query Params:** \?page=1&limit=20&status=completed\

- \GET /api/surveys/{survey_id}/export\
  - **Mô tả:** Render dữ liệu bài test dưới dạng \	ext/csv\ để tải xuống máy.

- \GET /api/surveys/{survey_id}/analytics\
  - **Mô tả:** Gọi aggregation query đếm số đáp án đúng / sai từng \question_id\ để trả về câu làm sai/đúng nhiều nhất.
