import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Страница 3 из ARCHITECTURE.md: Регистрация нового читателя (/register)
 * Содержит Форму 2 (username, email, password, password_confirm) с клиентской проверкой совпадения паролей.
 */
export default function RegisterPage({ onLoginSuccess }) {
  const navigate = useNavigate();

  // Поля формы регистрации
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');

  // Состояния загрузки и ошибок
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');

    // Простая клиентская валидация перед отправкой на сервер
    if (password.length < 4) {
      setError('Пароль должен содержать минимум 4 символа.');
      return;
    }

    if (password !== passwordConfirm) {
      setError('Пароли не совпадают! Проверьте правильность ввода.');
      return;
    }

    setLoading(true);
    try {
      const data = await apiFetch('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({
          username,
          email,
          password,
          password_confirm: passwordConfirm,
        }),
      });

      // Бэкенд сразу возвращает token и user — сохраняем их и авторизуем студента
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      if (onLoginSuccess) {
        onLoginSuccess(data.user);
      }

      navigate('/');
    } catch (err) {
      setError(err.message || 'Ошибка при регистрации пользователя.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="form-box card">
      <h1 className="page-title">Регистрация читателя</h1>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="reg-username">Имя пользователя (логин)</label>
          <input
            id="reg-username"
            type="text"
            className="input"
            placeholder="Например: ivan_petrov"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-email">Электронная почта (Email)</label>
          <input
            id="reg-email"
            type="email"
            className="input"
            placeholder="student@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-password">Пароль (минимум 4 символа)</label>
          <input
            id="reg-password"
            type="password"
            className="input"
            placeholder="Введите пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-password-confirm">Повторите пароль</label>
          <input
            id="reg-password-confirm"
            type="password"
            className="input"
            placeholder="Повторите пароль еще раз"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '8px' }}
          disabled={loading}
        >
          {loading ? 'Регистрируем...' : 'Зарегистрироваться'}
        </button>
      </form>

      <p style={{ marginTop: '16px', fontSize: '0.9rem', color: 'var(--muted-color)' }}>
        Уже есть аккаунт? <Link to="/login">Войти в систему</Link>
      </p>
    </div>
  );
}
