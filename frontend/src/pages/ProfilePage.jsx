import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Страница 5 из ARCHITECTURE.md: Личный кабинет читателя (/profile)
 * Реализует:
 * 1. Отображение данных текущего пользователя (логин, email, роль).
 * 2. Таблицу взятых книг (GET /api/v1/loans/) с фильтрацией и кнопкой «Вернуть книгу»
 *    (POST /api/v1/loans/{id}/return/), которая переводит статус в 'returned' и возвращает копию в каталог.
 * 3. Список всех отзывов, оставленных этим пользователем (GET /api/v1/reviews/?mine=true), с возможностью удаления.
 */
export default function ProfilePage({ user }) {
  const [loans, setLoans] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Загружаем список взятых книг и моих отзывов
  async function loadProfileData() {
    setLoading(true);
    setError('');
    try {
      const [loansData, reviewsData] = await Promise.all([
        apiFetch('/loans/'),
        apiFetch('/reviews/?mine=true'),
      ]);
      setLoans(Array.isArray(loansData) ? loansData : loansData.results || []);
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

  // Обработчик кнопки «Вернуть книгу» (POST /api/v1/loans/{id}/return/)
  async function handleReturnBook(loanId, bookTitle) {
    setError('');
    setSuccessMessage('');
    try {
      await apiFetch(`/loans/${loanId}/return/`, {
        method: 'POST',
      });
      setSuccessMessage(`Книга «${bookTitle}» успешно возвращена в библиотеку!`);
      await loadProfileData();
    } catch (err) {
      setError(err.message || 'Не удалось оформить возврат книги.');
    }
  }

  // Удаление собственного отзыва из личного кабинета
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

  // Форматирование даты для наглядного отображения в таблице
  function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('ru-RU');
  }

  return (
    <div>
      <h1 className="page-title">Личный кабинет читателя</h1>

      {/* Карточка профиля пользователя */}
      {user && (
        <div className="card">
          <h2 className="section-title">Профиль пользователя</h2>
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

      {/* Секция 1: Взятые книги (активные и история возвратов) */}
      <div className="card">
        <h2 className="section-title">Мои взятые книги ({loans.length})</h2>

        {loading ? (
          <p>Загрузка списка выдач...</p>
        ) : loans.length === 0 ? (
          <p style={{ color: 'var(--muted-color)' }}>
            У вас пока нет взятых книг. Перейдите в <Link to="/">каталог</Link>, чтобы выбрать книгу!
          </p>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Книга</th>
                  <th>Дата выдачи</th>
                  <th>Срок возврата</th>
                  <th>Дата возврата</th>
                  <th>Статус</th>
                  <th>Действие</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => {
                  const isActive = loan.status === 'active';
                  return (
                    <tr key={loan.id}>
                      <td>
                        <Link to={`/books/${loan.book}`}>
                          <strong>{loan.book_title || `Книга #${loan.book}`}</strong>
                        </Link>
                      </td>
                      <td>{formatDate(loan.borrowed_at)}</td>
                      <td>{formatDate(loan.due_at)}</td>
                      <td>{formatDate(loan.returned_at)}</td>
                      <td>
                        <span className={`badge ${isActive ? 'badge-out' : 'badge-available'}`}>
                          {isActive ? 'На руках' : 'Возвращена'}
                        </span>
                      </td>
                      <td>
                        {isActive ? (
                          <button
                            type="button"
                            className="btn btn-success"
                            onClick={() => handleReturnBook(loan.id, loan.book_title)}
                          >
                            Вернуть книгу
                          </button>
                        ) : (
                          <span style={{ color: 'var(--muted-color)', fontSize: '0.88rem' }}>
                            Сдана в архив
                          </span>
                        )}
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
