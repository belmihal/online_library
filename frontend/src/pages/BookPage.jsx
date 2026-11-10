import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api.js';

/**
 * Страница 4 из ARCHITECTURE.md: Детальная страница книги (/books/:id)
 * Реализует:
 * 1. Просмотр полной информации о книге, авторах, жанрах, рейтинге и наличии экземпляров.
 * 2. Форму 4: Выдача книги читателю (выбор даты возврата due_at + кнопка «Взять книгу»).
 * 3. Список всех отзывов читателей по этой книге.
 * 4. Форму 3: Добавление собственного отзыва (оценка 1..5 и комментарий) и удаление своего отзыва.
 */
export default function BookPage({ user }) {
  const { id } = useParams();

  // Данные книги и списка отзывов
  const [book, setBook] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Состояния для Формы 4 (Взять книгу в библиотеке)
  const [dueDate, setDueDate] = useState(() => {
    // По умолчанию предлагаем дату возврата через 14 дней в формате YYYY-MM-DD
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });
  const [loanLoading, setLoanLoading] = useState(false);
  const [loanMessage, setLoanMessage] = useState('');
  const [loanError, setLoanError] = useState('');

  // Состояния для Формы 3 (Оставить отзыв о книге)
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewMessage, setReviewMessage] = useState('');
  const [reviewError, setReviewError] = useState('');

  // Функция загрузки данных книги и её отзывов с сервера
  async function loadBookAndReviews() {
    setLoading(true);
    setError('');
    try {
      const [bookData, reviewsData] = await Promise.all([
        apiFetch(`/books/${id}/`),
        apiFetch(`/reviews/?book=${id}`),
      ]);
      setBook(bookData);
      setReviews(Array.isArray(reviewsData) ? reviewsData : reviewsData.results || []);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить данные книги.');
    } finally {
      setLoading(false);
    }
  }

  // Загружаем книгу при открытии страницы или смене ID в адресной строке
  useEffect(() => {
    loadBookAndReviews();
  }, [id]);

  // Обработчик Формы 4: Взять книгу (POST /api/v1/loans/)
  async function handleBorrowBook(event) {
    event.preventDefault();
    setLoanError('');
    setLoanMessage('');

    if (!dueDate) {
      setLoanError('Пожалуйста, укажите дату возврата книги.');
      return;
    }

    setLoanLoading(true);
    try {
      await apiFetch('/loans/', {
        method: 'POST',
        body: JSON.stringify({
          book: Number(id),
          due_at: dueDate,
        }),
      });

      setLoanMessage('Книга успешно оформлена! Вы можете увидеть её в разделе «Мои книги и отзывы».');
      // Перезагружаем данные книги, чтобы счетчик свободных копий (available_copies) уменьшился на 1
      await loadBookAndReviews();
    } catch (err) {
      setLoanError(err.message || 'Ошибка при оформлении выдачи книги.');
    } finally {
      setLoanLoading(false);
    }
  }

  // Обработчик Формы 3: Оставить отзыв (POST /api/v1/reviews/)
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
      setReviewMessage('Спасибо! Ваш отзыв опубликован, средний рейтинг книги пересчитан.');
      // Перезагружаем книгу и список отзывов, чтобы сразу увидеть новый avg_rating
      await loadBookAndReviews();
    } catch (err) {
      setReviewError(err.message || 'Не удалось отправить отзыв.');
    } finally {
      setReviewLoading(false);
    }
  }

  // Удаление собственного отзыва (или любого отзыва, если вошел администратор)
  async function handleDeleteReview(reviewId) {
    setReviewError('');
    setReviewMessage('');
    try {
      await apiFetch(`/reviews/${reviewId}/`, {
        method: 'DELETE',
      });
      setReviewMessage('Отзыв удален, рейтинг книги обновлен.');
      await loadBookAndReviews();
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

  const isAvailable = book.available_copies > 0;

  return (
    <div>
      <div style={{ marginBottom: '16px' }}>
        <Link to="/" className="btn btn-outline">
          ← Назад в каталог
        </Link>
      </div>

      {/* Карточка с подробным описанием книги */}
      <div className="card">
        <h1 className="page-title">{book.title}</h1>

        <div className="badges-row" style={{ marginBottom: '12px' }}>
          <span className="badge">⭐ Средний рейтинг: {Number(book.avg_rating || 0).toFixed(2)}</span>
          <span className={`badge ${isAvailable ? 'badge-available' : 'badge-out'}`}>
            {isAvailable
              ? `Доступно для выдачи: ${book.available_copies} из ${book.total_copies}`
              : 'Нет свободных экземпляров'}
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

      {/* Форма 4: Оформление выдачи книги читателю */}
      <div className="card">
        <h2 className="section-title">Взять книгу в библиотеке</h2>

        {loanError && <div className="alert alert-error">{loanError}</div>}
        {loanMessage && <div className="alert alert-success">{loanMessage}</div>}

        {!user ? (
          <p>
            Чтобы взять книгу на чтение, пожалуйста, <Link to="/login">войдите в систему</Link> или{' '}
            <Link to="/register">зарегистрируйтесь</Link>.
          </p>
        ) : (
          <form onSubmit={handleBorrowBook} style={{ maxWidth: '420px' }}>
            <div className="form-group">
              <label htmlFor="loan-due-date">Срок возврата (до какой даты планируете читать)</label>
              <input
                id="loan-due-date"
                type="date"
                className="input"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={!isAvailable || loanLoading}
            >
              {loanLoading
                ? 'Оформляем выдачу...'
                : isAvailable
                ? '📖 Взять книгу'
                : 'Нет свободных экземпляров'}
            </button>
          </form>
        )}
      </div>

      {/* Секция отзывов и Форма 3 (Добавление нового отзыва) */}
      <div className="card">
        <h2 className="section-title">Отзывы читателей ({reviews.length})</h2>

        {reviewError && <div className="alert alert-error">{reviewError}</div>}
        {reviewMessage && <div className="alert alert-success">{reviewMessage}</div>}

        {/* Форма 3 показывается авторизованным пользователям */}
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

        {/* Список опубликованных отзывов */}
        {reviews.length === 0 ? (
          <p style={{ color: 'var(--muted-color)' }}>
            На эту книгу пока нет отзывов. Станьте первым!
          </p>
        ) : (
          <div className="books-list">
            {reviews.map((rev) => {
              const canDelete =
                user && (user.role === 'admin' || user.id === rev.user);
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
