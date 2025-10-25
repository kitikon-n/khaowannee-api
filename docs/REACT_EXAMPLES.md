# React API Integration Examples
## Vite + React - Complete Code Examples

## 📁 Project Structure

```
frontend/
├── src/
│   ├── services/
│   │   └── api.js           # API service
│   ├── context/
│   │   └── AuthContext.jsx  # Auth context
│   ├── components/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── ProtectedRoute.jsx
│   └── App.jsx
```

---

## 🔧 1. API Service (`src/services/api.js`)

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// สร้าง axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor สำหรับเพิ่ม Authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor สำหรับจัดการ errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token หมดอายุ - redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  // Register
  register: async (userData) => {
    const response = await api.post('/user/register', userData);
    return response.data;
  },

  // Login
  login: async (credentials) => {
    const response = await api.post('/user/login', credentials);
    const { access_token, refresh_token } = response.data;

    // เก็บ tokens ใน localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/user/me');
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Check if user is logged in
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

// Protected API calls
export const protectedAPI = {
  getProtectedData: async () => {
    const response = await api.get('/user/protected');
    return response.data;
  },
};

export default api;
```

---

## 🎯 2. Auth Context (`src/context/AuthContext.jsx`)

```jsx
// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ตรวจสอบ authentication เมื่อ app เริ่มต้น
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      if (authAPI.isAuthenticated()) {
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      authAPI.logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      await authAPI.login({ username, password });
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const register = async (userData) => {
    try {
      await authAPI.register(userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## 📝 3. Register Component (`src/components/Register.jsx`)

```jsx
// src/components/Register.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    user_name: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (formData.user_name.length < 3 || formData.user_name.length > 20) {
      setError('Username must be 3-20 characters');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    // Call API
    const result = await register(formData);
    setLoading(false);

    if (result.success) {
      alert('Registration successful! Please login.');
      navigate('/login');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            name="user_name"
            value={formData.user_name}
            onChange={handleChange}
            placeholder="3-20 characters"
            required
            minLength={3}
            maxLength={20}
          />
        </div>

        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="your@email.com"
            required
          />
        </div>

        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Minimum 6 characters"
            required
            minLength={6}
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>

      <p>
        Already have an account? <a href="/login">Login here</a>
      </p>
    </div>
  );
};

export default Register;
```

---

## 🔐 4. Login Component (`src/components/Login.jsx`)

```jsx
// src/components/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(formData.username, formData.password);
    setLoading(false);

    if (result.success) {
      navigate('/dashboard'); // redirect to dashboard
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Enter your username"
            required
          />
        </div>

        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p>
        Don't have an account? <a href="/register">Register here</a>
      </p>
    </div>
  );
};

export default Login;
```

---

## 🛡️ 5. Protected Route Component

```jsx
// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

---

## 📱 6. Dashboard Component (Protected)

```jsx
// src/components/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { protectedAPI } from '../services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [protectedData, setProtectedData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProtectedData = async () => {
    setLoading(true);
    try {
      const data = await protectedAPI.getProtectedData();
      setProtectedData(data);
    } catch (error) {
      console.error('Failed to fetch protected data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>

      <div className="user-info">
        <h3>User Information</h3>
        <p><strong>User ID:</strong> {user?.user_id}</p>
        <p><strong>Username:</strong> {user?.user_name}</p>
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Status:</strong> {user?.active ? 'Active' : 'Inactive'}</p>
      </div>

      <button onClick={fetchProtectedData} disabled={loading}>
        {loading ? 'Loading...' : 'Fetch Protected Data'}
      </button>

      {protectedData && (
        <div className="protected-data">
          <h3>Protected Data</h3>
          <pre>{JSON.stringify(protectedData, null, 2)}</pre>
        </div>
      )}

      <button onClick={logout} className="logout-btn">
        Logout
      </button>
    </div>
  );
};

export default Dashboard;
```

---

## 🚀 7. Main App Setup (`src/App.jsx`)

```jsx
// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

---

## 📦 8. Required Dependencies

```bash
npm install axios react-router-dom
```

```json
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  }
}
```

---

## 🎨 9. Basic Styling (Optional)

```css
/* src/index.css */
.login-container,
.register-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.error-message {
  color: red;
  margin: 10px 0;
  padding: 10px;
  background-color: #fee;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}
```

---

## ✅ Complete Flow

1. User เข้า **Register page** → กรอกข้อมูล → สมัครสมาชิก
2. Redirect ไป **Login page** → กรอก username/password → Login
3. ได้ **Token** → เก็บใน localStorage
4. Redirect ไป **Dashboard** (Protected Route)
5. ดึงข้อมูล user และ protected data ได้
6. กด **Logout** → ลบ token → redirect to login

---

## 🔍 Debugging Tips

```javascript
// ดู token ใน console
console.log('Access Token:', localStorage.getItem('access_token'));

// ดู request headers
api.interceptors.request.use(config => {
  console.log('Request:', config);
  return config;
});

// ดู response
api.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
});
```

---

ทุกอย่างพร้อมแล้ว! Copy code ไปใช้ได้เลยครับ 🚀
