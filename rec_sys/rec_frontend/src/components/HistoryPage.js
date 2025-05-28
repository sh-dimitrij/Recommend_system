import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import ProfilePopup from './ProfilePopup';
import './HistoryPage.css';

export default function HistoryPage({ token }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('http://localhost:8000/api/history/', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => {
      setHistory(res.data);
    }).catch(console.error)
      .finally(() => setLoading(false));

    // Загружаем данные пользователя
    axios.get('http://localhost:8000/api/user/', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setUserData(res.data))
      .catch(console.error);
  }, [token]);

  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };

  if (loading) return <p>Загрузка...</p>;

  return (
    <>
      {/* Кнопка меню */}
      <button
        className={`nav-button ${navOpen ? "open" : ""}`}
        onClick={() => setNavOpen(!navOpen)}
        aria-label="Открыть навигацию"
      >
        {navOpen ? "×" : "≡"}
      </button>

      {/* Кнопка профиля */}
      <button
        className="profile-button"
        onClick={() => setProfileOpen(true)}
        aria-label="Профиль"
      >
        <img
          className="profile-avatar"
          src="https://www.w3schools.com/howto/img_avatar.png"
          alt="profile"
        />
      </button>

      {/* Боковая панель */}
      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} onNavigate={handleNavigate} />

      {/* Попап профиля */}
      <ProfilePopup
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        user={userData}
        logout={() => {
          localStorage.removeItem("accessToken");
          window.location.reload();
        }}
      />

      <div className="history-wrapper" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        padding: '20px',
      }}>
        {history.length === 0 && <p>История пуста.</p>}
        {history.map(item => (
          <div key={item.id} className="history-card" style={{
            border: "1px solid #ccc",
            padding: "20px",
            borderRadius: "8px",
            width: "80%",
            maxWidth: "700px",
            backgroundColor: "#f9f9f9",
            boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
          }}>
            <h3>{item.title}</h3>
            <p>Автор: {item.author}</p>
            <a href={item.link} target="_blank" rel="noopener noreferrer">
              Подробнее
            </a>
            <p style={{ fontSize: '0.8em', color: '#666' }}>
              {new Date(item.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}
