import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Личный кабинет читателя LitHub (/profile)
 * Реализует:
 * 1. Карточку профиля текущего пользователя.
 * 2. Секцию «Моя книжная полка» (GET /api/v1/shelf/) с кнопкой «Убрать с полки» (DELETE /api/v1/shelf/{id}/).
 * 3. Секцию «Мои отзывы» (GET /api/v1/reviews/?mine=true) с возможностью удаления.
 */
export default function ProfilePage({ user }) {
  const [shelfItems, setShelfItems] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Загружаем книги на полке пользователя и его отзывы
  async function loadProfileData() {
    setLoading(true);
    setError('');
    try {
      const [shelfData, reviewsData] = await Promise.all([
        apiFetch('/shelf/'),
        apiFetch('/reviews/?mine=true'),
      ]);
      setShelfItems(Array.isArray(shelfData) ? shelfData : shelfData.results || []);
      setMyReviews(Array.isArray(reviewsData) ? reviewsData : reviewsData.results || []);
    } catch (err) {
      setError(err.message || 'Ошибка при загрузке данных личного кабинета.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfileData();
  }, []);

  // Удаление книги с личной книжной полки (DELETE /api/v1/shelf/{id}/)
  async function handleRemoveFromShelf(shelfItemId, bookTitle) {
    setError('');
    setSuccessMessage('');
    try {
      await apiFetch(`/shelf/${shelfItemId}/`, {
        method: 'DELETE',
      });
      setSuccessMessage(`Книга «${bookTitle}» убрана с вашей полки.`);
      await loadProfileData();
    } catch (err) {
      setError(err.message || 'Не удалось убрать книгу с полки.');
    }
  }

  // Удаление собственного отзыва
  async function handleDeleteMyReview(reviewId) {
    setError('');
    setSuccessMessage('');
    try {
      await apiFetch(`/reviews/${reviewId}/`, {
        method: 'DELETE',
      });
      setSuccessMessage('Ваш отзыв успешно удален.');
      await loadProfileData();
    } catch (err) {
      setError(err.message || 'Не удалось удалить отзыв.');
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('ru-RU');
  }

  return (
    <div>
      <h1 className="page-title">Моя полка и отзывы</h1>

      {/* Карточка профиля пользователя */}
      {user && (
        <div className="card">
          <h2 className="section-title">Профиль читателя LitHub</h2>
          <p>
            <strong>Логин:</strong> {user.username} • <strong>Email:</strong> {user.email} •{' '}
            <strong>Роль:</strong>{' '}
            <span className="badge">
              {user.role === 'admin' ? 'Администратор' : 'Читатель'}
            </span>
          </p>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {/* Секция 1: Моя книжная полка */}
      <div className="card">
        <h2 className="section-title">Моя книжная полка ({shelfItems.length})</h2>

        {loading ? (
          <p>Загрузка вашей книжной полки...</p>
        ) : shelfItems.length === 0 ? (
          <p style={{ color: 'var(--muted-color)' }}>
            На вашей полке пока нет сохранённых книг. Перейдите в <Link to="/">каталог LitHub</Link>,
            чтобы добавить интересующие книги!
          </p>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Книга</th>
                  <th>Авторы</th>
                  <th>Дата добавления</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {shelfItems.map((item) => {
                  const authorsText =
                    Array.isArray(item.book_authors) && item.book_authors.length > 0
                      ? item.book_authors.join(', ')
                      : 'Автор не указан';
                  return (
                    <tr key={item.id}>
                      <td>
                        <Link to={`/books/${item.book}`}>
                          <strong>{item.book_title || `Книга #${item.book}`}</strong>
                        </Link>
                      </td>
                      <td>{authorsText}</td>
                      <td>{formatDate(item.added_at)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          <Link to={`/books/${item.book}`} className="btn btn-primary">
                            📖 Читать
                          </Link>
                          <button
                            type="button"
                            className="btn btn-outline"
                            onClick={() => handleRemoveFromShelf(item.id, item.book_title)}
                          >
                            Убрать с полки
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Секция 2: Мои отзывы */}
      <div className="card">
        <h2 className="section-title">Мои отзывы ({myReviews.length})</h2>

        {loading ? (
          <p>Загрузка ваших отзывов...</p>
        ) : myReviews.length === 0 ? (
          <p style={{ color: 'var(--muted-color)' }}>
            Вы еще не оставляли отзывов на книги.
          </p>
        ) : (
          <div className="books-list">
            {myReviews.map((rev) => (
              <div
                key={rev.id}
                style={{
                  padding: '14px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '12px',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700 }}>
                    <Link to={`/books/${rev.book}`}>
                      {rev.book_title || `Книга #${rev.book}`}
                    </Link>{' '}
                    • <span className="badge">Оценка: {rev.rating}/5</span>
                  </div>
                  <p style={{ marginTop: '6px' }}>{rev.comment}</p>
                </div>

                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={() => handleDeleteMyReview(rev.id)}
                >
                  Удалить отзыв
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
