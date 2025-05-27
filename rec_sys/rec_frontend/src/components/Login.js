import React, { useState } from 'react';
import "./Login.css";

const Login = ({ setUserData }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok && data.access) {
        localStorage.setItem('accessToken', data.access);

        const userResponse = await fetch('http://localhost:8000/api/user/', {
          headers: {
            Authorization: `Bearer ${data.access}`
          }
        });

        const userData = await userResponse.json();
        setUserData(userData);
        setError(null);
      } else {
        setError(data.detail || 'Неверные логин или пароль');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    }
  };

  return (
    <div className="login-page">
      <form className="login-form" onSubmit={handleLogin}>
        <h2>Вход</h2>
        {error && <p className="err">{error}</p>}
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Логин"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль"
          required
        />
        <button type="submit">Войти</button>
      </form>
    </div>
  );
};

export default Login;
