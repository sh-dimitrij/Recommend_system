import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from './Sidebar';    
import ProfilePopup from "./ProfilePopup"; // если ещё нет – просто верни пустой заглушкой
import "./Home.css";
import SurveyForm from "./SurveyForm";

export default function Home({ userData }) {
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };

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
      {/* поп‑ап профиля (можно пока вернуть null) */}
      <ProfilePopup
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        user={userData}
        logout={() => {
          localStorage.removeItem("accessToken");
          window.location.reload();
        }}
      />


      {/* центральная часть */}
      <div className="main-container">
        <SurveyForm userData={userData} />  
      </div>
    </>
  );
}
