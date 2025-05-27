import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Home from './components/Home';
import GradeList from './components/GradeList';

function App() {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      fetch('http://localhost:8000/api/user/', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
        .then(res => {
          if (!res.ok) throw new Error('Token invalid');
          return res.json();
        })
        .then(data => setUserData(data))
        .catch(() => {
          localStorage.removeItem('accessToken');
          setUserData(null);
        });
    }
  }, []);

  if (userData === null) {
    // Пока проверяем авторизацию, можно показать загрузку
    return <div>Загрузка...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        {!userData ? (
          <>
            <Route path="/login" element={<Login setUserData={setUserData} />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </>
        ) : (
          <>
            <Route path="/" element={<Home userData={userData} />} />
            <Route path="/grades" element={<GradeList token={localStorage.getItem('accessToken')} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
