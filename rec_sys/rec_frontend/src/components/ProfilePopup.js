// src/components/ProfilePopup.js
import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import { FaUserCircle } from "react-icons/fa";
import "./ProfilePopup.css";

export default function ProfilePopup({ open, onClose }) {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  if (!open) return null;

  return (
    <div className="profile-popup-overlay" onClick={onClose}>
      <div className="profile-popup" onClick={(e) => e.stopPropagation()}>
        <div className="profile-header">
          <FaUserCircle className="popup-avatar" size={58} />
          <h2>Профиль</h2>
        </div>

        {user ? (
          <>
            <table className="profile-table">
              <tbody>
                <tr><td>ФИО</td><td>{user.full_name}</td></tr>
                <tr><td>Группа</td><td>{user.group}</td></tr>
                <tr><td>Факультет</td><td>{user.faculty}</td></tr>
                <tr><td>Кафедра</td><td>{user.department}</td></tr>
                <tr><td>Курс</td><td>{user.course}</td></tr>
                <tr><td>Семестр</td><td>{user.semester}</td></tr>
                <tr><td>Год поступления</td><td>{user.year_of_entry}</td></tr>
              </tbody>
            </table>
            <button className="close-button" onClick={logout}>Выйти</button>
          </>
        ) : (
          <>
            <p>Вы не авторизованы.</p>
            <button
              className="close-button"
              onClick={() => {
                onClose();
                navigate("/login");
              }}
            >
              Войти
            </button>
          </>
        )}
      </div>
    </div>
  );
}
