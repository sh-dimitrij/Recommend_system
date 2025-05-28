import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from './Sidebar';
import ProfilePopup from './ProfilePopup';
import './DeadlinesPage.css';

export default function DeadlinesPage({ userData }) {
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    axios.get('http://localhost:8000/api/deadlines/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => setDeadlines(res.data))
    .catch(err => console.error('Ошибка загрузки дедлайнов', err))
    .finally(() => setLoading(false));
  }, []);

  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };
    // Функция для поиска ближайшего дедлайна
    const getNearestDeadline = (deadlines) => {
        const now = new Date();
        const futureDeadlines = deadlines
          .filter(d => d.deadline && new Date(d.deadline) >= now);
    
        if (futureDeadlines.length === 0) return null;
    
        futureDeadlines.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
        return futureDeadlines[0];
      };

  if (loading) return <div>Загрузка...</div>;

        const activeDeadlines = deadlines.filter(d => !d.is_completed);

        const nearestDeadline = getNearestDeadline(activeDeadlines);
        const otherDeadlines = nearestDeadline
        ? activeDeadlines.filter(d => d.id !== nearestDeadline.id)
        : activeDeadlines;



  return (
    <>
      <button
        className={`nav-button ${navOpen ? 'open' : ''}`}
        onClick={() => setNavOpen(!navOpen)}
        aria-label="Открыть навигацию"
      >
        {navOpen ? '×' : '≡'}
      </button>

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

      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} onNavigate={handleNavigate} />
      <ProfilePopup
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        user={userData}
        logout={() => {
          localStorage.removeItem('accessToken');
          window.location.reload();
        }}
      />

      <div className="deadlines-wrapper">
        <h2 style={{ textAlign: 'center' }}>Сроки выполнения работ</h2>

        {nearestDeadline && (
          <div className="nearest-deadline" style={{
            background: '#fffae6',
            border: '2px solid #f0c040',
            borderRadius: '10px',
            padding: '20px',
            marginBottom: '30px',
            maxWidth: '600px',
            marginLeft: 'auto',
            marginRight: 'auto',
            boxShadow: '0 0 10px rgba(240,192,64,0.5)'
          }}>
            <h3>Ближайший дедлайн</h3>
            <h4>{nearestDeadline.title}</h4>
            <p>Тип работы: {nearestDeadline.type}</p>
            <p> {nearestDeadline.module || 'Не указан'}</p>
            <p>Срок сдачи: {new Date(nearestDeadline.deadline).toLocaleDateString('ru-RU')}</p>
            <p>{nearestDeadline.description}</p>
          </div>
        )}

        <div className="deadlines-list">
        {otherDeadlines.length === 0 && !nearestDeadline && <p>Нет активных напоминаний.</p>}
        {otherDeadlines.map(item => (
            <div key={item.id} className="deadline-card">
            <h3>{item.title}</h3>
            <p>Тип работы: {item.type}</p>
            <p>{item.module || 'Не указан'}</p>
            <p>Срок сдачи: {item.deadline ? new Date(item.deadline).toLocaleDateString('ru-RU') : 'Дата не указана'}</p>
            <p>{item.description}</p>
            </div>
        ))}
        </div>
      </div>
    </>
  );
}
