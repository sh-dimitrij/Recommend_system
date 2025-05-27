import React from 'react';
import './Sidebar.css';

function Sidebar({ open, onClose, onNavigate }) {
  return (
    <>
      {open && <div className="backdrop" onClick={onClose} />}
      <div className={`sidebar ${open ? 'open' : ''}`}>
        <ul>
          <li onClick={() => onNavigate('/')}>Главная</li>
          <li onClick={() => onNavigate('/grades')}>Успеваемость</li>
          <li onClick={() => onNavigate('/')}>История</li>
          <li onClick={() => onNavigate('/')}>Дедлайны</li>
          <li onClick={() => onNavigate('/')}>Электронные книги</li>
        </ul>
      </div>
    </>
  );
}

export default Sidebar;
