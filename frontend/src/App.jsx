import React, { useEffect, useState } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom';
import { apiFetch } from './api.js';

import CatalogPage from './pages/CatalogPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import BookPage from './pages/BookPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import AdminPage from './pages/AdminPage.jsx';

/**
 * Корневой компонент приложения LitHub (src/App.jsx).
 * Отвечает за:
 * 1. Хранение текущего пользователя в localStorage и проверку сессии (/auth/me/)
 * 2. Переключение светлой и темной оранжевой темы (с сохранением в localStorage)
 * 3. Шапку навигации (Header) и маршрутизацию по всем 6 страницам через <BrowserRouter>
 */
export default function App() {
  // Читаем пользователя из localStorage при загрузке приложения
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    if (!savedUser) return null;
    try {
      return JSON.parse(savedUser);
    } catch {
      return null;
    }
  });

  // Состояние темы оформления: 'light' (светло-оранжевая) или 'dark' (тёмно-оранжевая)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  // Обновляем атрибут data-theme на <body> при смене темы
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Проверяем актуальный профиль пользователя по токену при загрузке страницы
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    apiFetch('/auth/me/')
      .then((meData) => {
        setUser(meData);
        localStorage.setItem('user', JSON.stringify(meData));
      })
      .catch(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
      });
  }, []);

  function toggleTheme() {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  }

  async function handleLogout() {
    try {
      await apiFetch('/auth/logout/', { method: 'POST' });
    } catch {
      // Игнорируем ошибку сети при выходе и очищаем данные локально
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }

  return (
    <BrowserRouter>
      {/* Шапка сайта LitHub с навигацией и переключателем темы */}
      <header className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="navbar-brand">
            📚 LitHub
          </Link>

          <nav className="navbar-links">
            <Link to="/" className="nav-link">
              Каталог книг
            </Link>

            {user && (
              <Link to="/profile" className="nav-link">
                Моя полка и отзывы
              </Link>
            )}

            {user && user.role === 'admin' && (
              <Link to="/admin" className="nav-link">
                Админ-панель
              </Link>
            )}

            <button
              type="button"
              className="btn btn-outline"
              onClick={toggleTheme}
              title="Переключить тему оформления"
            >
              {theme === 'light' ? '🌙 Темная тема' : '☀️ Светлая тема'}
            </button>

            {user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge">
                  👤 {user.username} ({user.role === 'admin' ? 'Админ' : 'Читатель'})
                </span>
                <button type="button" className="btn btn-outline" onClick={handleLogout}>
                  Выйти
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Link to="/login" className="btn btn-outline">
                  Вход
                </Link>
                <Link to="/register" className="btn btn-primary">
                  Регистрация
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      {/* Основная область контента с маршрутами всех 6 страниц */}
      <main className="container">
        <Routes>
          <Route path="/" element={<CatalogPage />} />
          <Route path="/login" element={<LoginPage onLoginSuccess={(u) => setUser(u)} />} />
          <Route path="/register" element={<RegisterPage onLoginSuccess={(u) => setUser(u)} />} />
          <Route path="/books/:id" element={<BookPage user={user} />} />
          <Route
            path="/profile"
            element={user ? <ProfilePage user={user} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/admin"
            element={
              user && user.role === 'admin' ? (
                <AdminPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
