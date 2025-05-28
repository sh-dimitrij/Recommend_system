import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from './Sidebar';
import ProfilePopup from './ProfilePopup';
import './EBooksPage.css';

export default function EBooksPage({ userData }) {
  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [ebooks, setEbooks] = useState([]);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const difficultyMap = {
    BEGINNER: 'Начинающий',
    INTERMEDIATE: 'Средний',
    ADVANCED: 'Продвинутый',
  };

  const handleNavigate = (path) => {
    navigate(path);
    setNavOpen(false);
  };

  const filteredEbooks = ebooks
  .filter(ebook =>
    ebook.title.toLowerCase().includes(search.toLowerCase()) ||
    ebook.author.toLowerCase().includes(search.toLowerCase())
  )
  .sort((a, b) => a.title.localeCompare(b.title));


  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get("http://localhost:8000/api/ebooks/", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setEbooks(res.data))
      .catch(err => console.error('Ошибка загрузки книг', err));
  }, []);

  return (
    <>
      <button
        className={`nav-button ${navOpen ? "open" : ""}`}
        onClick={() => setNavOpen(!navOpen)}
        aria-label="Открыть навигацию"
      >
        {navOpen ? "×" : "≡"}
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
          localStorage.removeItem("accessToken");
          window.location.reload();
        }}
      />

      <div className="ebooks-wrapper">
        <h2>Электронные книги</h2>
        <input
          type="text"
          placeholder="Поиск по названию..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="ebook-search"
        />
        <div className="ebooks-list">
          {filteredEbooks.map(book => (
            <div key={book.id} className="ebook-card">
              <h3>{book.title}</h3>
              <p>Автор: {book.author}</p>
              {/* <p>Сложность: {book.difficulty_level}</p> */}
              <p>Сложность: {difficultyMap[book.difficulty_level]}</p>
              {book.tags.length > 0 && (
                <div className="tags">
                  {book.tags.map(tag => (
                    <span key={tag.id} className="tag">{tag.name}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
