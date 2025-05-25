// src/components/Home.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";
import ProfilePopup from "./ProfilePopup";

function Sidebar({ open, onClose, handleNavigate }) {
  return (
    <>
      {open && <div className="backdrop" onClick={onClose} />}
      <div className={`sidebar ${open ? "open" : ""}`}>
        <ul>
          <li onClick={() => handleNavigate("/")}>Главная</li>
          <li onClick={() => handleNavigate("/history")}>История</li>
          <li onClick={() => handleNavigate("/deadlines")}>Дедлайны</li>
          <li onClick={() => handleNavigate("/ebooks")}>Электронные книги</li>
        </ul>
      </div>
    </>
  );
}

export default function Home() {
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };

  return (
    <>
      <button className={`nav-button ${navOpen ? "open" : ""}`} onClick={() => setNavOpen(!navOpen)}>
        {navOpen ? "×" : "≡"}
      </button>

      <button className="profile-button" onClick={() => setProfileOpen(true)}>
        <img className="profile-avatar" src="https://www.w3schools.com/howto/img_avatar.png" alt="profile" />
      </button>

      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} handleNavigate={handleNavigate} />
      <ProfilePopup open={profileOpen} onClose={() => setProfileOpen(false)} />

      <div className="main-container">
        <button className="important-button">Заполнить анкету</button>
      </div>
    </>
  );
}
