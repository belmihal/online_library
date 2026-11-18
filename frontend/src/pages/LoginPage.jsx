import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Страница входа в цифровую библиотеку LitHub (/login)
 */
export default function LoginPage({ onLoginSuccess }) {
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await apiFetch('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      if (onLoginSuccess) {
        onLoginSuccess(data.user);
      }

      navigate('/');
    } catch (err) {
      setError(err.message || 'Не удалось выполнить вход. Проверьте логин и пароль.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="form-box card">
      <h1 className="page-title">Вход в LitHub</h1>

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

      <div
        style={{
          marginTop: '18px',
          paddingTop: '12px',
          borderTop: '1px solid var(--border-color)',
          fontSize: '0.88rem',
          color: 'var(--muted-color)',
        }}
      >
        <p><strong>Демо-аккаунты LitHub для проверки:</strong></p>
        <p>• Читатель: <code>reader</code> / <code>reader123</code></p>
        <p>• Администратор: <code>admin</code> / <code>admin123</code></p>
        <p style={{ marginTop: '10px' }}>
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}
