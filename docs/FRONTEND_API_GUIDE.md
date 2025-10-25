# Frontend API Integration Guide
## Vite + React - Authentication APIs

## 📋 API Endpoints

### Base URL
```javascript
const API_BASE_URL = "http://localhost:8000"
```

---

## 🔐 Authentication APIs

### 1. Register (สมัครสมาชิก)

**Endpoint:** `POST /user/register`

**Request:**
```javascript
{
  "user_name": "john_doe",      // 3-20 ตัวอักษร
  "email": "john@example.com",   // Email format
  "password": "password123"      // ขั้นต่ำ 6 ตัวอักษร
}
```

**Response (201 Created):**
```javascript
{
  "user_id": 1,
  "user_name": "john_doe",
  "email": "john@example.com",
  "active": true,
  "created_date": "2025-10-25T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request` - Username already exists
- `422 Unprocessable Entity` - Validation error (รูปแบบข้อมูลไม่ถูกต้อง)

---

### 2. Login (เข้าสู่ระบบ)

**Endpoint:** `POST /user/login`

**Request:**
```javascript
{
  "username": "john_doe",
  "password": "password123"
}
```

**Response (200 OK):**
```javascript
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid username or password
- `403 Forbidden` - User account is inactive

---

### 3. Get Current User (ดูข้อมูลตัวเอง)

**Endpoint:** `GET /user/me`

**Headers:**
```javascript
{
  "Authorization": "Bearer <access_token>"
}
```

**Response (200 OK):**
```javascript
{
  "user_id": 1,
  "user_name": "john_doe",
  "email": "john@example.com",
  "active": true,
  "created_date": "2025-10-25T10:00:00"
}
```

**Error Responses:**
- `401 Unauthorized` - Token invalid หรือหมดอายุ
- `403 Forbidden` - User account is inactive

---

### 4. Protected Route (ตัวอย่าง)

**Endpoint:** `GET /user/protected`

**Headers:**
```javascript
{
  "Authorization": "Bearer <access_token>"
}
```

**Response (200 OK):**
```javascript
{
  "message": "Hello john_doe!",
  "user_id": 1,
  "email": "john@example.com",
  "status": "This is a protected route!"
}
```

---

## 🔄 Token Management

### Token Expiration
- **Access Token:** หมดอายุใน **30 นาที**
- **Refresh Token:** หมดอายุใน **7 วัน**

### Token Storage (แนะนำ)
```javascript
// เก็บใน localStorage
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// ดึงมาใช้
const token = localStorage.getItem('access_token');

// ลบเมื่อ logout
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

---

## 🚨 Error Handling

### Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | แสดงข้อมูล |
| 201 | Created | Redirect to login |
| 400 | Bad Request | แสดง error message |
| 401 | Unauthorized | Redirect to login, ลบ token |
| 403 | Forbidden | แสดง "Account inactive" |
| 422 | Validation Error | แสดง field errors |
| 500 | Server Error | แสดง "Something went wrong" |

### Error Response Format
```javascript
{
  "detail": "Error message here"
}

// หรือ validation errors
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## 🔧 CORS Configuration

Backend มีการตั้งค่า CORS แล้ว (`allow_origins=["*"]`)

ถ้าต้องการจำกัด origin:
```python
# ใน backend: app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/user/register \
  -H "Content-Type: application/json" \
  -d '{"user_name":"testuser","email":"test@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Get Current User
```bash
curl -X GET http://localhost:8000/user/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📱 Swagger UI (สำหรับทดสอบ)

เปิดเบราว์เซอร์:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 💡 Tips

1. **Always check token expiration** ก่อนเรียก API
2. **Handle 401 errors** โดย redirect ไป login page
3. **Store tokens securely** - ใช้ httpOnly cookies ใน production
4. **Implement token refresh** เมื่อ access token หมดอายุ
5. **Clear tokens on logout** เพื่อความปลอดภัย

---

## 🔗 Related Documents

- [React API Integration Examples](./REACT_EXAMPLES.md) - ตัวอย่างโค้ด React
- [Authentication Flow](./AUTH_FLOW.md) - Flow diagram
- [Error Handling Guide](./ERROR_HANDLING.md) - จัดการ errors
