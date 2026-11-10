import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Страница 2 из ARCHITECTURE.md: Вход в систему (/login)
 * Содержит Форму 1 (логин/email + пароль).
 * При успешном входе сохраняет token и user в localStorage и перенаправляет в каталог.
 */
export default function LoginPage({ onLoginSuccess }) {
  const navigate = useNavigate();

  // Состояния полей формы
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Состояния загрузки и текста ошибки
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Обработчик отправки формы входа
  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await apiFetch('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      // Сохраняем бессрочный токен и данные пользователя в localStorage
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Сообщаем родительскому компоненту App.jsx об успешном входе
      if (onLoginSuccess) {
        onLoginSuccess(data.user);
      }

      // Переходим на главную страницу каталога
      navigate('/');
    } catch (err) {
      setError(err.message || 'Не удалось выполнить вход. Проверьте логин и пароль.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="form-box card">
      <h1 className="page-title">Вход в библиотеку</h1>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="login-username">Логин или Email</label>
          <input
            id="login-username"
            type="text"
            className="input"
            placeholder="Например: reader или admin"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="login-password">Пароль</label>
          <input
            id="login-password"
            type="password"
            className="input"
            placeholder="Введите пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '8px' }}
          disabled={loading}
        >
          {loading ? 'Входим...' : 'Войти'}
        </button>
      </form>

      {/* Подсказка с демо-аккаунтами из команды seed_demo для удобной демонстрации на защите */}
      <div
        style={{
          marginTop: '18px',
          paddingTop: '12px',
          borderTop: '1px solid var(--border-color)',
          fontSize: '0.88rem',
          color: 'var(--muted-color)',
        }}
      >
        <p><strong>Демо-аккаунты для проверки:</strong></p>
        <p>• Читатель: <code>reader</code> / <code>reader123</code></p>
        <p>• Администратор: <code>admin</code> / <code>admin123</code></p>
        <p style={{ marginTop: '10px' }}>
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}
