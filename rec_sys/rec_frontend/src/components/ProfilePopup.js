import React from "react";
import { useNavigate } from "react-router-dom";
import "./ProfilePopup.css";

/**
 * Модальное окно профиля.
 * @param {{open: boolean, onClose: () => void, user: object|null, logout: () => void}} props
 */
export default function ProfilePopup({ open, onClose, user, logout }) {
  const navigate = useNavigate();

  if (!open) return null;

  // клик по затемнению закрывает поп‑ап
  const handleOverlayClick = () => onClose();
  // останавливаем всплытие внутри «карточки»
  const stop = (e) => e.stopPropagation();

  const handleLoginRedirect = () => {
    onClose();
    navigate("/login");
  };

  return (
    <div className="profile-popup-overlay" onClick={handleOverlayClick}>
      <div className="profile-popup" onClick={stop}>
        <div className="profile-header">
          {/* иконка FA заменена на встроенный emoji, чтобы не тянуть react‑icons */}
          <span role="img" aria-label="avatar" className="popup-avatar">👤</span>
          <h2>Профиль</h2>
        </div>

        {user ? (
          <>
            <table className="profile-table">
              <tbody>
                <tr><td>ФИО</td><td>{user.full_name}</td></tr>
                <tr><td>Группа</td><td>{user.group}</td></tr>
                <tr><td>Кафедра</td><td>{user.department ? `${user.department.name} (${user.department.short_name})` : '—'}</td></tr>
                <tr><td>Курс</td><td>{user.course}</td></tr>
                <tr><td>Семестр</td><td>{user.semester}</td></tr>
                <tr><td>Год поступления</td><td>{user.year_of_entry}</td></tr>
              </tbody>
            </table>
            <button className="close-button" onClick={logout}>Выйти</button>
          </>
        ) : (
          <>
            <p style={{ textAlign: "center" }}>Вы не авторизованы.</p>
            <button className="close-button" onClick={handleLoginRedirect}>Войти</button>
          </>
        )}
      </div>
    </div>
  );
}
