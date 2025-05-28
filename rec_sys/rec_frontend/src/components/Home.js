import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Sidebar from './Sidebar';    
import ProfilePopup from "./ProfilePopup"; 
import "./Home.css";
import SurveyForm from "./SurveyForm";

export default function Home({ userData }) {
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [recommendation, setRecommendation] = useState(null);
  const [nearestDeadline, setNearestDeadline] = useState(null);
  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    // Загрузка рекомендации
    axios.get("http://localhost:8000/api/recommendation/latest/", {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => setRecommendation(res.data))
    .catch(err => {
      if (err.response && err.response.status === 404) {
        setRecommendation(null);
      } else {
        console.error("Unexpected error", err);
      }
    });

    // Загрузка дедлайнов для ближайшего
    axios.get("http://localhost:8000/api/deadlines/", {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => {
      const deadlines = res.data;
      const now = new Date();
      const futureDeadlines = deadlines.filter(d => d.deadline && new Date(d.deadline) >= now);
      if (futureDeadlines.length === 0) {
        setNearestDeadline(null);
        return;
      }
      futureDeadlines.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
      setNearestDeadline(futureDeadlines[0]);
    })
    .catch(err => {
      console.error('Ошибка загрузки дедлайнов', err);
      setNearestDeadline(null);
    });
  }, []);

  return (
    <>
      {/* кнопка-бургер */}
      <button
        className={`nav-button ${navOpen ? "open" : ""}`}
        onClick={() => setNavOpen(!navOpen)}
        aria-label="Открыть навигацию"
      >
        {navOpen ? "×" : "≡"}
      </button>

      {/* кнопка профиля */}
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

      {/* боковое меню */}
      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} onNavigate={handleNavigate} />
      {/* поп‑ап профиля */}
      <ProfilePopup
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        user={userData}
        logout={() => {
          localStorage.removeItem("accessToken");
          window.location.reload();
        }}
      />

      <div className="content-wrapper" style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <SurveyForm userData={userData} setRecommendation={setRecommendation} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px', width: '320px', marginTop: '18vh' }}>
          {recommendation ? (
            <div className="recommendation-card" style={{
              border: "1px solid #ccc",
              padding: "16px",
              borderRadius: "8px",
              backgroundColor: "#f9f9f9"
            }}>
              <h3>Рекомендация для вас</h3>
              <p><strong>{recommendation.book_title}</strong></p>
              <p>Автор: {recommendation.book_author}</p>
              <a href={recommendation.book_link} target="_blank" rel="noopener noreferrer">
                Подробнее
              </a>
            </div>
          ) : (
            <p>Рекомендация пока не получена.</p>
          )}

          {nearestDeadline ? (
            <div className="nearest-deadline-card" style={{
              border: "1px solid #f0c040",
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: "#fff8d6",
              boxShadow: '0 0 8px rgba(240,192,64,0.4)'
            }}>
              <h4>Ближайший дедлайн</h4>
              <h5>{nearestDeadline.title}</h5>
              <p>Тип работы: {nearestDeadline.type}</p>
              <p>{nearestDeadline.module || 'Не указан'}</p>
              <p>Срок сдачи: {new Date(nearestDeadline.deadline).toLocaleDateString('ru-RU')}</p>
            </div>
          ) : (
            <p>Ближайший дедлайн не найден.</p>
          )}
        </div>
      </div>
    </>
  );
}
