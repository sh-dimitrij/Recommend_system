import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/current_user/', {
        method: 'GET',
        credentials: 'include', // <--- ОЧЕНЬ ВАЖНО!
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Ошибка получения пользователя:', error);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  // login
const login = async (username, password) => {
  const res = await fetch('http://localhost:8000/api/login/', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Неверный логин или пароль');
  setUser(await res.json());
};

// logout
const logout = async () => {
  await fetch('http://localhost:8000/api/logout/', {
    method: 'POST',
    credentials: 'include',
  });
  setUser(null);
};


  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
