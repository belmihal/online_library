import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch, uploadBooksCsv } from '../api.js';

/**
 * Страница 6 из ARCHITECTURE.md: Панель администратора (/admin)
 * Доступна только пользователям с ролью 'admin'.
 * Реализует:
 * 1. Форму 5: Добавление новой книги в каталог (с выбором авторов и жанров M2M).
 * 2. Импорт книг из CSV-файла (POST /api/v1/books/import-csv/) — пункт на доп. баллы.
 * 3. Таблицу управления всеми книгами с возможностью удаления книги (DELETE /api/v1/books/{id}/).
 */
export default function AdminPage() {
  // Списки книг, авторов и жанров
  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);

  // Уведомления об успехе и ошибках
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Поля Формы 5 (Создание новой книги)
  const [title, setTitle] = useState('');
  const [isbn, setIsbn] = useState('');
  const [publishedYear, setPublishedYear] = useState(2024);
  const [pages, setPages] = useState(250);
  const [publisher, setPublisher] = useState('АСТ');
  const [totalCopies, setTotalCopies] = useState(3);
  const [description, setDescription] = useState('');
  const [selectedAuthorIds, setSelectedAuthorIds] = useState([]);
  const [selectedGenreIds, setSelectedGenreIds] = useState([]);
  const [creatingBook, setCreatingBook] = useState(false);

  // Состояние для загрузки CSV-файла
  const [csvFile, setCsvFile] = useState(null);
  const [csvUploading, setCsvUploading] = useState(false);

  // Загрузка справочников и списка книг
  async function loadAdminData() {
    setLoading(true);
    try {
      const [booksData, authorsData, genresData] = await Promise.all([
        apiFetch('/books/?page_size=50'),
        apiFetch('/authors/'),
        apiFetch('/genres/'),
      ]);
      setBooks(Array.isArray(booksData) ? booksData : booksData.results || []);
      setAuthors(Array.isArray(authorsData) ? authorsData : authorsData.results || []);
      setGenres(Array.isArray(genresData) ? genresData : genresData.results || []);
    } catch (err) {
      setError(err.message || 'Ошибка при загрузке данных админ-панели.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAdminData();
  }, []);

  // Переключение чекбокса выбора автора (M2M)
  function toggleAuthorId(id) {
    setSelectedAuthorIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  }

  // Переключение чекбокса выбора жанра (M2M)
  function toggleGenreId(id) {
    setSelectedGenreIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  }

  // Обработчик Формы 5: Создание новой книги (POST /api/v1/books/)
  async function handleCreateBook(event) {
    event.preventDefault();
    setError('');
    setSuccessMessage('');
    setCreatingBook(true);

    try {
      await apiFetch('/books/', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          isbn: isbn.trim(),
          published_year: Number(publishedYear),
          pages: Number(pages),
          publisher: publisher.trim(),
          total_copies: Number(totalCopies),
          available_copies: Number(totalCopies),
          description: description.trim(),
          author_ids: selectedAuthorIds,
          genre_ids: selectedGenreIds,
        }),
      });

      setSuccessMessage(`Книга «${title}» успешно добавлена в каталог!`);
      // Очищаем поля формы
      setTitle('');
      setIsbn('');
      setDescription('');
      setSelectedAuthorIds([]);
      setSelectedGenreIds([]);

      await loadAdminData();
    } catch (err) {
      setError(err.message || 'Ошибка при создании книги.');
    } finally {
      setCreatingBook(false);
    }
  }

  // Обработчик импорта книг из CSV-файла (POST /api/v1/books/import-csv/)
  async function handleCsvUpload(event) {
    event.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!csvFile) {
      setError('Пожалуйста, выберите файл формата .csv для загрузки.');
      return;
    }

    setCsvUploading(true);
    try {
      const result = await uploadBooksCsv(csvFile);
      setSuccessMessage(
        result.detail || `Импорт завершен: создано ${result.created}, обновлено ${result.updated}.`
      );
      setCsvFile(null);
      await loadAdminData();
    } catch (err) {
      setError(err.message || 'Ошибка при импорте CSV-файла.');
    } finally {
      setCsvUploading(false);
    }
  }

  // Удаление книги из каталога (DELETE /api/v1/books/{id}/)
  async function handleDeleteBook(bookId, bookTitle) {
    setError('');
    setSuccessMessage('');
    try {
      await apiFetch(`/books/${bookId}/`, {
        method: 'DELETE',
      });
      setSuccessMessage(`Книга «${bookTitle}» удалена из каталога.`);
      await loadAdminData();
    } catch (err) {
      setError(err.message || 'Не удалось удалить книгу.');
    }
  }

  return (
    <div>
      <h1 className="page-title">Панель администратора библиотеки</h1>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {/* Блок 1: Импорт книг из CSV-файла */}
      <div className="card">
        <h2 className="section-title">Массовый импорт книг из CSV-файла</h2>
        <p style={{ fontSize: '0.9rem', color: 'var(--muted-color)', marginBottom: '12px' }}>
          Поддерживаются колонки: <code>title, isbn, published_year, publisher, pages, total_copies, description</code>.
        </p>

        <form
          onSubmit={handleCsvUpload}
          style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}
        >
          <input
            type="file"
            accept=".csv,text/csv"
            className="input"
            style={{ maxWidth: '360px' }}
            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
          />
          <button type="submit" className="btn btn-primary" disabled={csvUploading}>
            {csvUploading ? 'Загружаем CSV...' : '📥 Импортировать из CSV'}
          </button>
        </form>
      </div>

      {/* Блок 2: Форма 5 — Создание новой книги */}
      <div className="card">
        <h2 className="section-title">Добавить новую книгу в каталог</h2>

        <form onSubmit={handleCreateBook}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '12px',
            }}
          >
            <div className="form-group">
              <label htmlFor="book-title">Название книги *</label>
              <input
                id="book-title"
                type="text"
                className="input"
                placeholder="Например: Ревизор"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="book-isbn">ISBN (уникальный код) *</label>
              <input
                id="book-isbn"
                type="text"
                className="input"
                placeholder="978-5-17-099999-1"
                value={isbn}
                onChange={(e) => setIsbn(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="book-year">Год издания</label>
              <input
                id="book-year"
                type="number"
                className="input"
                value={publishedYear}
                onChange={(e) => setPublishedYear(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="book-pages">Количество страниц</label>
              <input
                id="book-pages"
                type="number"
                className="input"
                value={pages}
                onChange={(e) => setPages(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="book-publisher">Издательство</label>
              <input
                id="book-publisher"
                type="text"
                className="input"
                value={publisher}
                onChange={(e) => setPublisher(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="book-copies">Количество экземпляров</label>
              <input
                id="book-copies"
                type="number"
                min="1"
                className="input"
                value={totalCopies}
                onChange={(e) => setTotalCopies(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Выбор авторов (M2M) */}
          <div className="form-group" style={{ marginTop: '8px' }}>
            <label>Выберите авторов книги:</label>
            <div className="badges-row">
              {authors.map((a) => (
                <label
                  key={a.id}
                  className="badge"
                  style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                >
                  <input
                    type="checkbox"
                    checked={selectedAuthorIds.includes(a.id)}
                    onChange={() => toggleAuthorId(a.id)}
                  />
                  {a.full_name || `${a.first_name} ${a.last_name}`}
                </label>
              ))}
            </div>
          </div>

          {/* Выбор жанров (M2M) */}
          <div className="form-group">
            <label>Выберите жанры книги:</label>
            <div className="badges-row">
              {genres.map((g) => (
                <label
                  key={g.id}
                  className="badge"
                  style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                >
                  <input
                    type="checkbox"
                    checked={selectedGenreIds.includes(g.id)}
                    onChange={() => toggleGenreId(g.id)}
                  />
                  {g.name}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="book-desc">Описание книги</label>
            <textarea
              id="book-desc"
              className="textarea"
              placeholder="Краткая аннотация книги..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={creatingBook}>
            {creatingBook ? 'Сохраняем...' : '➕ Добавить книгу'}
          </button>
        </form>
      </div>

      {/* Блок 3: Таблица всех книг каталога */}
      <div className="card">
        <h2 className="section-title">Управление книгами в каталоге ({books.length})</h2>

        {loading ? (
          <p>Загрузка таблицы книг...</p>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Название</th>
                  <th>ISBN</th>
                  <th>Год</th>
                  <th>Копии (Доступно / Всего)</th>
                  <th>Рейтинг</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {books.map((b) => (
                  <tr key={b.id}>
                    <td>{b.id}</td>
                    <td>
                      <Link to={`/books/${b.id}`}>
                        <strong>{b.title}</strong>
                      </Link>
                    </td>
                    <td>{b.isbn}</td>
                    <td>{b.published_year}</td>
                    <td>
                      {b.available_copies} / {b.total_copies}
                    </td>
                    <td>⭐ {Number(b.avg_rating || 0).toFixed(1)}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-danger"
                        onClick={() => handleDeleteBook(b.id, b.title)}
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
