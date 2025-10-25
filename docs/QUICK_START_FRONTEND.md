# Quick Start - Frontend Integration
## เริ่มต้นใช้งาน API ใน 5 นาที

## 🚀 Setup (ครั้งเดียว)

### 1. ติดตั้ง Dependencies
```bash
npm install axios react-router-dom
```

### 2. สร้างไฟล์ API Service
สร้างไฟล์ `src/services/api.js` แล้ว copy code จาก `REACT_EXAMPLES.md`

### 3. เพิ่ม AuthProvider ใน App.jsx
```jsx
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      {/* your routes */}
    </AuthProvider>
  );
}
```

---

## 📝 การใช้งานเบื้องต้น

### 1. Register (สมัครสมาชิก)

```jsx
import { authAPI } from './services/api';

const handleRegister = async () => {
  try {
    const result = await authAPI.register({
      user_name: "testuser",
      email: "test@example.com",
      password: "password123"
    });
    console.log('Success:', result);
    // redirect to login
  } catch (error) {
    console.error('Error:', error.response?.data?.detail);
  }
};
```

### 2. Login (เข้าสู่ระบบ)

```jsx
import { authAPI } from './services/api';

const handleLogin = async () => {
  try {
    const result = await authAPI.login({
      username: "testuser",
      password: "password123"
    });
    console.log('Logged in!', result);
    // Token ถูกเก็บอัตโนมัติ
    // redirect to dashboard
  } catch (error) {
    console.error('Error:', error.response?.data?.detail);
  }
};
```

### 3. Get Current User

```jsx
import { authAPI } from './services/api';

const getCurrentUser = async () => {
  try {
    const user = await authAPI.getCurrentUser();
    console.log('User:', user);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### 4. Logout

```jsx
import { authAPI } from './services/api';

const handleLogout = () => {
  authAPI.logout();
  // redirect to login
};
```

---

## 🎯 ใช้กับ React Hooks

### ใช้ useAuth Hook

```jsx
import { useAuth } from './context/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return (
      <div>
        <p>Welcome, {user.user_name}!</p>
        <button onClick={logout}>Logout</button>
      </div>
    );
  }

  return <button onClick={() => login('user', 'pass')}>Login</button>;
}
```

---

## 🔐 Protected Routes

```jsx
import ProtectedRoute from './components/ProtectedRoute';

<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

---

## ⚡ Fetch และแสดงข้อมูล

```jsx
import { useState, useEffect } from 'react';
import { authAPI } from './services/api';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>{user.user_name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

---

## 🐛 Debugging

### ดู Token
```javascript
console.log(localStorage.getItem('access_token'));
```

### ดู Request
```javascript
// ใน api.js
api.interceptors.request.use(config => {
  console.log('📤 Request:', config.url, config.data);
  return config;
});
```

### ดู Response
```javascript
api.interceptors.response.use(response => {
  console.log('📥 Response:', response.data);
  return response;
});
```

---

## ❌ Error Handling

```jsx
try {
  await authAPI.login({ username, password });
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Error:', error.response.data.detail);

    switch (error.response.status) {
      case 400:
        alert('Bad request');
        break;
      case 401:
        alert('Invalid credentials');
        break;
      case 403:
        alert('Account inactive');
        break;
      default:
        alert('Something went wrong');
    }
  } else if (error.request) {
    // No response from server
    alert('Cannot connect to server');
  } else {
    // Other errors
    alert('Error: ' + error.message);
  }
}
```

---

## 🎨 Form Validation

```jsx
const [errors, setErrors] = useState({});

const validate = () => {
  const newErrors = {};

  if (formData.user_name.length < 3) {
    newErrors.user_name = 'Username must be at least 3 characters';
  }

  if (!/\S+@\S+\.\S+/.test(formData.email)) {
    newErrors.email = 'Invalid email format';
  }

  if (formData.password.length < 6) {
    newErrors.password = 'Password must be at least 6 characters';
  }

  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};

const handleSubmit = async (e) => {
  e.preventDefault();
  if (!validate()) return;

  // Submit form...
};
```

---

## 🔄 Auto-redirect หลัง Login

```jsx
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(username, password);

    if (result.success) {
      navigate('/dashboard'); // ✅ redirect to dashboard
    }
  };
};
```

---

## 📋 Checklist

- ✅ ติดตั้ง axios และ react-router-dom
- ✅ สร้างไฟล์ `src/services/api.js`
- ✅ สร้างไฟล์ `src/context/AuthContext.jsx`
- ✅ เพิ่ม `<AuthProvider>` ใน App.jsx
- ✅ สร้าง Login component
- ✅ สร้าง Register component
- ✅ สร้าง ProtectedRoute component
- ✅ เพิ่ม routes ใน App.jsx
- ✅ ทดสอบ Register → Login → Dashboard

---

## 🎓 Next Steps

1. เพิ่ม **Loading states** ให้สวยงาม
2. เพิ่ม **Toast notifications** สำหรับ success/error
3. เพิ่ม **Form validation** ที่ละเอียดขึ้น
4. เพิ่ม **Token refresh** mechanism
5. เพิ่ม **Remember me** feature
6. เพิ่ม **Password strength indicator**

---

## 📚 เอกสารเพิ่มเติม

- [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md) - รายละเอียด API
- [REACT_EXAMPLES.md](./REACT_EXAMPLES.md) - ตัวอย่างโค้ดเต็ม
- [ERROR_HANDLING.md](./ERROR_HANDLING.md) - จัดการ errors

---

**Happy Coding! 🚀**
