import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login   from './components/Login';
import Home    from './components/Home';
import GradeList from './components/GradeList';
import HistoryPage from './components/HistoryPage';
import EBooksPage from './components/EBooksPage';
import DeadlinesPage from './components/DeadlinesPage';



function App() {
  const [userData, setUserData] = useState(null);   // данные пользователя или null
  const [loading, setLoading] = useState(true);     // идёт проверка токена

  useEffect(() => {
    const token = localStorage.getItem('accessToken');

    if (!token) {
      // нет токена → закончить проверку
      setLoading(false);
      return;
    }

    fetch('http://localhost:8000/api/user/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Token invalid');
        return res.json();
      })
      .then(data => setUserData(data))
      .catch(() => {
        localStorage.removeItem('accessToken');
        setUserData(null);
      })
      .finally(() => setLoading(false));   // в любом случае проверка окончена
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return (
    <BrowserRouter>
      <Routes>
        {userData ? (
          <>
            <Route path="/"        element={<Home userData={userData} />} />
            <Route path="/grades"  element={<GradeList token={localStorage.getItem('accessToken')} />} />
            <Route path="/history" element={<HistoryPage token={localStorage.getItem('accessToken')} />} />
            <Route path="/ebooks" element={<EBooksPage userData={userData} />} />
            <Route path="/deadlines" element={<DeadlinesPage token={localStorage.getItem('accessToken')} />} />
            <Route path="*"        element={<Navigate to="/" />} />
          </>
        ) : (
          <>
            <Route path="/login" element={<Login setUserData={setUserData} />} />
            <Route path="*"      element={<Navigate to="/login" />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
    