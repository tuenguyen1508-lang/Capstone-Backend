# API Endpoints Plan (RESTful CRUD)

Tài liệu định nghĩa các API dựa trên **database schema** hiện tại.\
Các API được thiết kế theo chuẩn **RESTful**, bao gồm đầy đủ **CRUD
(Create, Read, Update, Delete)** cho các entity trong hệ thống.

------------------------------------------------------------------------

# 0. Authentication & User Management

## Register

POST `/api/auth/register`

Payload

``` json
{
  "email": "researcher@test.com",
  "password": "123456",
  "role": "RESEARCHER"
}
```

Response

``` json
{
  "id": "uuid",
  "email": "researcher@test.com",
  "created_at": "timestamp"
}
```

------------------------------------------------------------------------

## Login

POST `/api/auth/login`

Payload

``` json
{
  "email": "researcher@test.com",
  "password": "123456"
}
```

Response

``` json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

------------------------------------------------------------------------

## Get Current User

GET `/api/auth/me`

Auth: Bearer Token

Response

``` json
{
  "id": "uuid",
  "email": "researcher@test.com",
  "roles": ["ADMIN"]
}
```

------------------------------------------------------------------------

# 1. File Upload

API để upload ảnh câu hỏi / đáp án lên Cloudflare R2.

POST `/upload/file`

POST `/upload/image`

Auth: Bearer Token

Form Data

    file: binary file/image

Query Params

    folder: uploads | images (optional)

Response

``` json
{
  "filename": "image.jpg",
  "key": "images/abc123...jpg",
  "url": "https://pub-xxx.r2.dev/images/abc123...jpg",
  "content_type": "image/jpeg",
  "size": 12345
}
```

------------------------------------------------------------------------

# 2. Survey Management

Auth: Bearer Token (ADMIN / RESEARCHER)

------------------------------------------------------------------------

## Get Surveys

GET `/api/surveys`

Response

``` json
[
  {
    "id": "uuid",
    "name": "Semester Quiz",
    "token": "uuid",
    "created_by": "user_id",
    "status": "active",
    "start_time": "timestamp",
    "end_time": "timestamp"
  }
]
```

------------------------------------------------------------------------

## Create Survey

POST `/api/surveys`

Payload

``` json
{
  "name": "Semester 1 Quiz",
  "start_time": "2026-03-01T00:00:00Z",
  "end_time": "2026-04-01T00:00:00Z",
  "status": "pending"
}
```

Response

``` json
{
  "id": "uuid",
  "token": "public_token"
}
```

------------------------------------------------------------------------

## Get Survey Detail

GET `/api/surveys/{survey_id}`

Response

``` json
{
  "id": "uuid",
  "name": "Semester 1 Quiz",
  "questions": []
}
```

------------------------------------------------------------------------

## Update Survey

PUT `/api/surveys/{survey_id}`

Payload

``` json
{
  "name": "Updated name",
  "status": "active"
}
```

------------------------------------------------------------------------

## Delete Survey

DELETE `/api/surveys/{survey_id}`

------------------------------------------------------------------------

# 3. Question Management

Auth: Bearer Token

------------------------------------------------------------------------

## Get Questions

GET `/api/surveys/{survey_id}/questions`

------------------------------------------------------------------------

## Create Question

POST `/api/surveys/{survey_id}/questions`

### MCQ

``` json
{
  "type": "mcq",
  "title": "Which drawing is correct?",
  "question_image": "https://r2/q1.jpg",
  "order_index": 1,
  "options": [
    {
      "image_url": "https://r2/opt1.jpg",
      "order_index": 1
    },
    {
      "image_url": "https://r2/opt2.jpg",
      "order_index": 2
    }
  ]
}
```

### Arrow Question

``` json
{
  "type": "arrow",
  "title": "Point to the stop sign",
  "question_image": "https://r2/q2.jpg",
  "order_index": 2,
  "config": {
    "correct_angle": 120.5,
    "tolerance": 15.0,
    "standing_position": "car",
    "looking_direction": "traffic light"
  }
}
```

------------------------------------------------------------------------

## Update Question

PUT `/api/questions/{question_id}`

Payload tương tự Create.

------------------------------------------------------------------------

## Delete Question

DELETE `/api/questions/{question_id}`

------------------------------------------------------------------------

# 4. Public Survey APIs

Các API dành cho học sinh làm bài.

------------------------------------------------------------------------

## Get Survey by Token

GET `/api/public/surveys/{token}`

Lưu ý: Không trả về `correct_angle`.

------------------------------------------------------------------------

## Participant Submit (Create/Update)

POST `/api/public/participants/submit`

Payload

``` json
{
  "survey_id": "uuid",
  "participant_id": "uuid (optional)",
  "code": "01",
  "name": "Jiara Martins",
  "school": "Ambience Public School",
  "grade": "6",
  "dob": "2012-05-15T00:00:00Z"
}
```

Rules

-   Bắt buộc có `survey_id` để xác định học sinh tham gia survey nào.
-   `participant_id` có giá trị: cập nhật hồ sơ participant.
-   `participant_id` rỗng: tạo mới (hoặc upsert theo cặp `survey_id` + `code`).

Response

``` json
{
  "id": "uuid",
  "survey_id": "uuid",
  "participant_id": "uuid (optional)",
  "code": "01",
  "name": "Jiara Martins",
  "school": "Ambience Public School",
  "grade": "6",
  "dob": "2012-05-15T00:00:00Z"
}
```

------------------------------------------------------------------------

## Get Participant (Read)

GET `/api/public/surveys/{survey_id}/participants/{participant_id}`

Hoặc tra theo code:

GET `/api/public/surveys/{survey_id}/participants/by-code/{code}`

Response

``` json
{
  "participant_id": "uuid",
  "survey_id": "uuid",
  "code": "01",
  "name": "Jiara Martins",
  "school": "Ambience Public School",
  "grade": "6",
  "dob": "2012-05-15T00:00:00Z"
}
```

------------------------------------------------------------------------

## Delete Participant

DELETE `/api/public/surveys/{survey_id}/participants/{participant_id}`

------------------------------------------------------------------------

## Start Attempt

POST `/api/public/surveys/{survey_id}/attempts/start`

Payload

``` json
{
  "participant_id": "uuid"
}

Response

``` json
{
  "attempt_id": "uuid",
  "start_time": "timestamp"
}
```

------------------------------------------------------------------------

## Save Answers

POST `/api/public/attempts/{attempt_id}/answers`

Payload

``` json
{
  "answers": [
    {
      "question_id": "uuid",
      "selected_option_id": "uuid",
      "user_angle": null
    },
    {
      "question_id": "uuid",
      "selected_option_id": null,
      "user_angle": 130.5
    }
  ]
}
```

------------------------------------------------------------------------

## Submit Attempt

PUT `/api/public/attempts/{attempt_id}/submit`

Response

``` json
{
  "score": 8.5,
  "status": "completed"
}
```

------------------------------------------------------------------------

# 5. Results & Analytics

Auth: Bearer Token

------------------------------------------------------------------------

## Get Survey Results

GET `/api/surveys/{survey_id}/results`

Query

    ?page=1&limit=20&status=completed

------------------------------------------------------------------------

## Export Results

GET `/api/surveys/{survey_id}/export`

Response

    text/csv

------------------------------------------------------------------------

## Survey Analytics

GET `/api/surveys/{survey_id}/analytics`

Response

``` json
{
  "questions": [
    {
      "question_id": "uuid",
      "correct_count": 30,
      "wrong_count": 12
    }
  ]
}
```

------------------------------------------------------------------------

# Database Schema Reference

    users
    roles
    user_roles
    surveys
    questions
    question_options
    question_config
    participants
    attempts
    answers
