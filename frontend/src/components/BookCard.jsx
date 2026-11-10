import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Компонент карточки книги (src/components/BookCard.jsx).
 * Отображает одну книгу в каталоге как в режиме «Плитка» (grid), так и в режиме «Список» (list).
 */
export default function BookCard({ book, viewMode = 'grid' }) {
  // Формируем строку с именами авторов книги
  const authorsText =
    book.authors && book.authors.length > 0
      ? book.authors.map((a) => a.full_name || `${a.first_name} ${a.last_name}`).join(', ')
      : 'Автор не указан';

  // Проверяем, есть ли свободные экземпляры для выдачи
  const isAvailable = book.available_copies > 0;

  return (
    <div className={`book-card ${viewMode === 'list' ? 'book-card-list' : ''}`}>
      {/* Блок обложки: если cover_url задан — показываем картинку, иначе стильную заглушку */}
      {book.cover_url ? (
        <img
          src={book.cover_url}
          alt={book.title}
          className="book-cover"
        />
      ) : (
        <div className="book-cover">
          <span>📚 {book.title}</span>
        </div>
      )}

      {/* Основная информация о книге */}
      <div style={{ flex: 1 }}>
        <div className="book-title">
          <Link to={`/books/${book.id}`}>{book.title}</Link>
        </div>

        <div className="book-meta">
          <strong>Автор:</strong> {authorsText} • <strong>Год:</strong> {book.published_year}
        </div>

        {/* Бейджи жанров */}
        <div className="badges-row">
          {book.genres &&
            book.genres.map((genre) => (
              <span key={genre.id} className="badge">
                {genre.name}
              </span>
            ))}
        </div>

        {/* Краткое описание (обрезаем до 120 символов для аккуратности карточки) */}
        {book.description && (
          <p style={{ fontSize: '0.9rem', marginBottom: '8px' }}>
            {book.description.length > 120
              ? `${book.description.slice(0, 120)}...`
              : book.description}
          </p>
        )}

        {/* Рейтинг и наличие экземпляров */}
        <div className="badges-row" style={{ alignItems: 'center' }}>
          <span className="badge">
            ⭐ Рейтинг: {Number(book.avg_rating || 0).toFixed(1)}
          </span>

          <span className={`badge ${isAvailable ? 'badge-available' : 'badge-out'}`}>
            {isAvailable
              ? `В наличии: ${book.available_copies} из ${book.total_copies}`
              : 'Нет свободных копий'}
          </span>
        </div>
      </div>

      {/* Кнопка перехода к подробной странице книги */}
      <div>
        <Link to={`/books/${book.id}`} className="btn btn-primary">
          Подробнее
        </Link>
      </div>
    </div>
  );
}
