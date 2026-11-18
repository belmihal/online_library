import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Детальная страница цифровой книги LitHub (/books/:id)
 * Реализует:
 * 1. Полную информацию о книге, авторах, жанрах и среднем рейтинге.
 * 2. Блок «Цифровой доступ к книге»:
 *    - Добавление книги на личную полку (POST /api/v1/shelf/) или удаление с полки (DELETE /api/v1/shelf/{id}/)
 *    - Встроенную онлайн-читалку («📖 Читать онлайн») с настройкой размера шрифта (A- / A+)
 * 3. Список отзывов читателей и форму добавления/удаления отзыва (POST/DELETE /api/v1/reviews/).
 */
export default function BookPage({ user }) {
  const { id } = useParams();

  // Данные книги и отзывов
  const [book, setBook] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Состояния для блока «Цифровой доступ к книге» (личная книжная полка + встроенная читалка)
  const [shelfItem, setShelfItem] = useState(null);
  const [shelfLoading, setShelfLoading] = useState(false);
  const [shelfMessage, setShelfMessage] = useState('');
  const [shelfError, setShelfError] = useState('');
  const [isReaderOpen, setIsReaderOpen] = useState(false);
  const [readerFontSize, setReaderFontSize] = useState(17);

  // Состояния для формы отзыва
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewMessage, setReviewMessage] = useState('');
  const [reviewError, setReviewError] = useState('');

  // Загружаем данные книги, её отзывы и проверяем, есть ли книга на полке текущего пользователя
  async function loadPageData() {
    setLoading(true);
    setError('');
    try {
      const [bookData, reviewsData] = await Promise.all([
        apiFetch(`/books/${id}/`),
        apiFetch(`/reviews/?book=${id}`),
      ]);
      setBook(bookData);
      setReviews(Array.isArray(reviewsData) ? reviewsData : reviewsData.results || []);

      if (user) {
        const shelfData = await apiFetch('/shelf/');
        const shelfList = Array.isArray(shelfData) ? shelfData : shelfData.results || [];
        const existingItem = shelfList.find((item) => item.book === Number(id)) || null;
        setShelfItem(existingItem);
      } else {
        setShelfItem(null);
      }
    } catch (err) {
      setError(err.message || 'Не удалось загрузить данные книги.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPageData();
  }, [id, user]);

  // Добавить книгу на мою полку (POST /api/v1/shelf/)
  async function handleAddToShelf() {
    setShelfError('');
    setShelfMessage('');
    setShelfLoading(true);

    try {
      const createdItem = await apiFetch('/shelf/', {
        method: 'POST',
        body: JSON.stringify({ book: Number(id) }),
      });
      setShelfItem(createdItem);
      setShelfMessage('Книга добавлена на вашу книжную полку LitHub!');
    } catch (err) {
      setShelfError(err.message || 'Не удалось добавить книгу на полку.');
    } finally {
      setShelfLoading(false);
    }
  }

  // Убрать книгу с моей полки (DELETE /api/v1/shelf/{shelfItemId}/)
  async function handleRemoveFromShelf() {
    if (!shelfItem) return;
    setShelfError('');
    setShelfMessage('');
    setShelfLoading(true);

    try {
      await apiFetch(`/shelf/${shelfItem.id}/`, {
        method: 'DELETE',
      });
      setShelfItem(null);
      setShelfMessage('Книга убрана с вашей книжной полки.');
    } catch (err) {
      setShelfError(err.message || 'Не удалось убрать книгу с полки.');
    } finally {
      setShelfLoading(false);
    }
  }

  // Добавить новый отзыв (POST /api/v1/reviews/)
  async function handleAddReview(event) {
    event.preventDefault();
    setReviewError('');
    setReviewMessage('');

    if (rating < 1 || rating > 5) {
      setReviewError('Оценка должна быть от 1 до 5.');
      return;
    }

    setReviewLoading(true);
    try {
      await apiFetch('/reviews/', {
        method: 'POST',
        body: JSON.stringify({
          book: Number(id),
          rating: Number(rating),
          comment: comment.trim(),
        }),
      });

      setComment('');
      setRating(5);
      setReviewMessage('Спасибо! Ваш отзыв опубликован, средний рейтинг книги обновлен.');
      await loadPageData();
    } catch (err) {
      setReviewError(err.message || 'Не удалось отправить отзыв.');
    } finally {
      setReviewLoading(false);
    }
  }

  // Удалить свой отзыв (или любой отзыв от имени администратора)
  async function handleDeleteReview(reviewId) {
    setReviewError('');
    setReviewMessage('');
    try {
      await apiFetch(`/reviews/${reviewId}/`, {
        method: 'DELETE',
      });
      setReviewMessage('Отзыв удален, средний рейтинг книги обновлен.');
      await loadPageData();
    } catch (err) {
      setReviewError(err.message || 'Не удалось удалить отзыв.');
    }
  }

  if (loading) {
    return <div className="card">Загрузка информации о книге...</div>;
  }

  if (error || !book) {
    return (
      <div className="card">
        <div className="alert alert-error">{error || 'Книга не найдена'}</div>
        <Link to="/" className="btn btn-outline">
          ← Вернуться в каталог
        </Link>
      </div>
    );
  }

  const authorsText =
    book.authors && book.authors.length > 0
      ? book.authors.map((a) => a.full_name || `${a.first_name} ${a.last_name}`).join(', ')
      : 'Автор не указан';

  return (
    <div>
      <div style={{ marginBottom: '16px' }}>
        <Link to="/" className="btn btn-outline">
          ← Назад в каталог
        </Link>
      </div>

      {/* Карточка с подробным описанием цифровой книги */}
      <div className="card">
        <h1 className="page-title">{book.title}</h1>

        <div className="badges-row" style={{ marginBottom: '12px' }}>
          <span className="badge">⭐ Средний рейтинг: {Number(book.avg_rating || 0).toFixed(2)}</span>
          <span className="badge badge-digital">
            📱 Цифровое издание • {book.pages} стр.
          </span>
          {book.genres &&
            book.genres.map((g) => (
              <span key={g.id} className="badge">
                {g.name}
              </span>
            ))}
        </div>

        <p style={{ marginBottom: '8px' }}>
          <strong>Авторы:</strong> {authorsText}
        </p>
        <p style={{ marginBottom: '8px' }}>
          <strong>ISBN:</strong> {book.isbn} • <strong>Год издания:</strong> {book.published_year} •{' '}
          <strong>Страниц:</strong> {book.pages} • <strong>Язык:</strong> {book.language}
        </p>
        {book.publisher && (
          <p style={{ marginBottom: '12px' }}>
            <strong>Издательство:</strong> {book.publisher}
          </p>
        )}

        <p style={{ marginTop: '12px', lineHeight: 1.6 }}>
          {book.description || 'Описание для этой книги пока не добавлено.'}
        </p>
      </div>

      {/* Блок «Цифровой доступ к книге»: личная полка + встроенная онлайн-читалка */}
      <div className="card">
        <h2 className="section-title">Цифровой доступ к книге</h2>

        {shelfError && <div className="alert alert-error">{shelfError}</div>}
        {shelfMessage && <div className="alert alert-success">{shelfMessage}</div>}

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Кнопка встроенной онлайн-читалки доступна сразу */}
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setIsReaderOpen((prev) => !prev)}
          >
            {isReaderOpen ? '📕 Закрыть читалку' : '📖 Читать онлайн'}
          </button>

          {/* Кнопки управления книжной полкой LitHub */}
          {!user ? (
            <span style={{ color: 'var(--muted-color)', fontSize: '0.92rem' }}>
              <Link to="/login">Войдите</Link> или <Link to="/register">зарегистрируйтесь</Link>, чтобы
              сохранить книгу на свою полку.
            </span>
          ) : shelfItem ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <span className="badge badge-digital" style={{ padding: '7px 12px', fontSize: '0.88rem' }}>
                ✓ Книга на вашей полке
              </span>
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleRemoveFromShelf}
                disabled={shelfLoading}
              >
                {shelfLoading ? 'Обновляем...' : 'Убрать с полки'}
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="btn btn-outline"
              onClick={handleAddToShelf}
              disabled={shelfLoading}
            >
              {shelfLoading ? 'Добавляем...' : '➕ Добавить на мою полку'}
            </button>
          )}
        </div>

        {/* Раскрывающийся блок встроенной читалки с настройкой размера шрифта (A- / A+) */}
        {isReaderOpen && (
          <div className="reader-box">
            <div className="reader-toolbar">
              <div>
                <strong>{book.title}</strong> — <span style={{ color: 'var(--muted-color)' }}>{authorsText}</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted-color)' }}>
                  Шрифт: {readerFontSize}px
                </span>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setReaderFontSize((size) => Math.max(13, size - 2))}
                  title="Уменьшить шрифт"
                >
                  A-
                </button>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setReaderFontSize((size) => Math.min(28, size + 2))}
                  title="Увеличить шрифт"
                >
                  A+
                </button>
              </div>
            </div>

            <div className="reader-content" style={{ fontSize: `${readerFontSize}px` }}>
              <p style={{ fontWeight: 700, marginBottom: '10px' }}>
                Ознакомительный фрагмент цифрового издания LitHub
              </p>
              <p style={{ marginBottom: '12px' }}>
                {book.description ||
                  'Электронный текст произведения доступен в цифровой библиотеке LitHub.'}
              </p>
              <p style={{ color: 'var(--muted-color)', fontSize: '0.9em' }}>
                Издание: {book.publisher || 'LitHub Digital'}, {book.published_year} г. • Объем:{' '}
                {book.pages} стр. • ISBN {book.isbn}.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Секция отзывов и форма добавления нового отзыва */}
      <div className="card">
        <h2 className="section-title">Отзывы читателей ({reviews.length})</h2>

        {reviewError && <div className="alert alert-error">{reviewError}</div>}
        {reviewMessage && <div className="alert alert-success">{reviewMessage}</div>}

        {user ? (
          <form
            onSubmit={handleAddReview}
            style={{
              marginBottom: '24px',
              paddingBottom: '20px',
              borderBottom: '1px solid var(--border-color)',
            }}
          >
            <h3 style={{ fontSize: '1.05rem', marginBottom: '12px' }}>Оставить свой отзыв</h3>

            <div className="form-group" style={{ maxWidth: '240px' }}>
              <label htmlFor="review-rating">Ваша оценка (от 1 до 5)</label>
              <select
                id="review-rating"
                className="select"
                value={rating}
                onChange={(e) => setRating(Number(e.target.value))}
              >
                <option value={5}>5 — Отлично (Шедевр)</option>
                <option value={4}>4 — Хорошо</option>
                <option value={3}>3 — Нормально</option>
                <option value={2}>2 — Слабо</option>
                <option value={1}>1 — Плохо</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="review-comment">Текст отзыва</label>
              <textarea
                id="review-comment"
                className="textarea"
                placeholder="Поделитесь впечатлениями о книге..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={reviewLoading}>
              {reviewLoading ? 'Публикуем...' : 'Опубликовать отзыв'}
            </button>
          </form>
        ) : (
          <p style={{ marginBottom: '18px' }}>
            <Link to="/login">Войдите в аккаунт</Link>, чтобы оставить оценку и отзыв о книге.
          </p>
        )}

        {reviews.length === 0 ? (
          <p style={{ color: 'var(--muted-color)' }}>
            На эту книгу пока нет отзывов. Станьте первым!
          </p>
        ) : (
          <div className="books-list">
            {reviews.map((rev) => {
              const canDelete = user && (user.role === 'admin' || user.id === rev.user);
              return (
                <div
                  key={rev.id}
                  style={{
                    padding: '14px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: '12px',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700, marginBottom: '4px' }}>
                      👤 {rev.username || `Пользователь #${rev.user}`} •{' '}
                      <span className="badge">Оценка: {'⭐'.repeat(rev.rating)} ({rev.rating}/5)</span>
                    </div>
                    <p style={{ marginTop: '6px' }}>{rev.comment}</p>
                    {rev.created_at && (
                      <div style={{ fontSize: '0.8rem', color: 'var(--muted-color)', marginTop: '6px' }}>
                        Дата: {new Date(rev.created_at).toLocaleDateString('ru-RU')}
                      </div>
                    )}
                  </div>

                  {canDelete && (
                    <button
                      type="button"
                      className="btn btn-danger"
                      onClick={() => handleDeleteReview(rev.id)}
                    >
                      Удалить
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
