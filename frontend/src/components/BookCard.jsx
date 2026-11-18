import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Компонент карточки цифровой книги LitHub (src/components/BookCard.jsx).
 * Отображает книгу в каталоге в режиме «Плитка» (grid) или «Список» (list).
 */
export default function BookCard({ book, viewMode = 'grid' }) {
  // Формируем строку с именами авторов книги
  const authorsText =
    book.authors && book.authors.length > 0
      ? book.authors.map((a) => a.full_name || `${a.first_name} ${a.last_name}`).join(', ')
      : 'Автор не указан';

  return (
    <div className={`book-card ${viewMode === 'list' ? 'book-card-list' : ''}`}>
      {/* Блок обложки: картинка по cover_url или аккуратная заглушка */}
      {book.cover_url ? (
        <img src={book.cover_url} alt={book.title} className="book-cover" />
      ) : (
        <div className="book-cover">
          <span>📚 {book.title}</span>
        </div>
      )}

      {/* Основная информация о цифровой книге */}
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

        {/* Краткая аннотация книги */}
        {book.description && (
          <p style={{ fontSize: '0.9rem', marginBottom: '8px' }}>
            {book.description.length > 120
              ? `${book.description.slice(0, 120)}...`
              : book.description}
          </p>
        )}

        {/* Рейтинг и бейдж цифрового издания */}
        <div className="badges-row" style={{ alignItems: 'center' }}>
          <span className="badge">
            ⭐ Рейтинг: {Number(book.avg_rating || 0).toFixed(1)}
          </span>

          <span className="badge badge-digital">
            📱 Цифровая книга • {book.pages} стр.
          </span>
        </div>
      </div>

      {/* Кнопка перехода на страницу книги */}
      <div>
        <Link to={`/books/${book.id}`} className="btn btn-primary">
          Открыть книгу
        </Link>
      </div>
    </div>
  );
}
