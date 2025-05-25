// src/App.js
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import Home from "./components/Home";
import Login from './components/Login';  // Убраны фигурные скобки

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} /> {/* ← новая страница */}
          <Route path="/history"    element={<div>История</div>} />
          <Route path="/deadlines"  element={<div>Дедлайны</div>} />
          <Route path="/ebooks"     element={<div>Электронные книги</div>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
