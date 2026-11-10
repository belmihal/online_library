import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api.js';
import BookCard from '../components/BookCard.jsx';

/**
 * Страница 1 из ARCHITECTURE.md: Каталог книг (/)
 * Реализует:
 * - Поиск по названию/ISBN/автору (?search=)
 * - Фильтрацию по жанру (?genre=), автору (?author=) и наличию (?available=true)
 * - Сортировку (?ordering=)
 * - Пагинацию страниц (?page=)
 * - Переключение режима отображения «Плитка / Список» с сохранением в localStorage
 */
export default function CatalogPage() {
  // Списки книг, жанров и авторов с бэкенда
  const [books, setBooks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [authors, setAuthors] = useState([]);

  // Параметры фильтрации, поиска и пагинации
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedAuthor, setSelectedAuthor] = useState('');
  const [ordering, setOrdering] = useState('-id');
  const [onlyAvailable, setOnlyAvailable] = useState(false);
  const [page, setPage] = useState(1);

  // Общее количество книг и наличие соседних страниц пагинации DRF
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);

  // Режим отображения карточек: 'grid' (Плитка) или 'list' (Список)
  const [viewMode, setViewMode] = useState(() => {
    return localStorage.getItem('catalogViewMode') || 'grid';
  });

  // Состояния загрузки и ошибок
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // При первом рендере загружаем справочники жанров и авторов для выпадающих списков
  useEffect(() => {
    async function loadDictionaries() {
      try {
        const [genresData, authorsData] = await Promise.all([
          apiFetch('/genres/'),
          apiFetch('/authors/'),
        ]);
        setGenres(Array.isArray(genresData) ? genresData : genresData.results || []);
        setAuthors(Array.isArray(authorsData) ? authorsData : authorsData.results || []);
      } catch (err) {
        console.error('Не удалось загрузить справочники жанров/авторов:', err);
      }
    }
    loadDictionaries();
  }, []);

  // Загружаем список книг при каждом изменении фильтров, поиска, сортировки или номера страницы
  useEffect(() => {
    async function loadBooks() {
      setLoading(true);
      setError('');
      try {
        const params = new URLSearchParams();
        if (search.trim()) params.set('search', search.trim());
        if (selectedGenre) params.set('genre', selectedGenre);
        if (selectedAuthor) params.set('author', selectedAuthor);
        if (ordering) params.set('ordering', ordering);
        if (onlyAvailable) params.set('available', 'true');
        params.set('page', String(page));

        const data = await apiFetch(`/books/?${params.toString()}`);

        // Поддерживаем как пагинированный ответ DRF ({ count, next, previous, results }), так и обычный массив
        if (Array.isArray(data)) {
          setBooks(data);
          setTotalCount(data.length);
          setHasNext(false);
          setHasPrev(false);
        } else {
          setBooks(data.results || []);
          setTotalCount(data.count || 0);
          setHasNext(Boolean(data.next));
          setHasPrev(Boolean(data.previous));
        }
      } catch (err) {
        setError(err.message || 'Ошибка при загрузке каталога книг.');
      } finally {
        setLoading(false);
      }
    }

    loadBooks();
  }, [search, selectedGenre, selectedAuthor, ordering, onlyAvailable, page]);

  // Переключение вида «Плитка / Список» с сохранением выбора в localStorage
  function handleChangeViewMode(mode) {
    setViewMode(mode);
    localStorage.setItem('catalogViewMode', mode);
  }

  // Сброс всех фильтров к значениям по умолчанию
  function handleResetFilters() {
    setSearch('');
    setSelectedGenre('');
    setSelectedAuthor('');
    setOrdering('-id');
    setOnlyAvailable(false);
    setPage(1);
  }

  return (
    <div>
      <h1 className="page-title">Каталог книг</h1>

      {/* Панель поиска и фильтрации */}
      <div className="card">
        <div className="filters-bar">
          <div>
            <label htmlFor="search-input" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
              Поиск по названию, ISBN или автору
            </label>
            <input
              id="search-input"
              type="text"
              className="input"
              placeholder="Введите название книги или фамилию автора..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div>
            <label htmlFor="genre-select" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
              Жанр
            </label>
            <select
              id="genre-select"
              className="select"
              value={selectedGenre}
              onChange={(e) => {
                setSelectedGenre(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Все жанры</option>
              {genres.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="author-select" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
              Автор
            </label>
            <select
              id="author-select"
              className="select"
              value={selectedAuthor}
              onChange={(e) => {
                setSelectedAuthor(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Все авторы</option>
              {authors.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.full_name || `${a.first_name} ${a.last_name}`}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="sort-select" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
              Сортировка
            </label>
            <select
              id="sort-select"
              className="select"
              value={ordering}
              onChange={(e) => {
                setOrdering(e.target.value);
                setPage(1);
              }}
            >
              <option value="-id">Сначала новые</option>
              <option value="-avg_rating">По рейтингу (убывание)</option>
              <option value="title">По названию (А-Я)</option>
              <option value="-published_year">По году издания (новые)</option>
            </select>
          </div>

          <div>
            <button type="button" className="btn btn-outline" onClick={handleResetFilters}>
              Сбросить
            </button>
          </div>
        </div>

        {/* Нижняя строка панели: чекбокс «Только в наличии» и переключатель «Плитка / Список» */}
        <div className="toolbar-row" style={{ marginBottom: 0 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={onlyAvailable}
              onChange={(e) => {
                setOnlyAvailable(e.target.checked);
                setPage(1);
              }}
            />
            <span>Показать только книги в наличии (доступные для выдачи)</span>
          </label>

          <div className="view-toggle">
            <button
              type="button"
              className={`btn ${viewMode === 'grid' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => handleChangeViewMode('grid')}
            >
              ⊞ Плитка
            </button>
            <button
              type="button"
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => handleChangeViewMode('list')}
            >
              ☰ Список
            </button>
          </div>
        </div>
      </div>

      {/* Информация о количестве найденных книг */}
      <div className="toolbar-row">
        <span style={{ color: 'var(--muted-color)', fontWeight: 500 }}>
          Найдено книг: <strong>{totalCount}</strong>
        </span>
      </div>

      {/* Вывод ошибки или индикатора загрузки */}
      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="card">Загрузка каталога книг...</div>
      ) : books.length === 0 ? (
        <div className="card">
          По вашему запросу книги не найдены. Попробуйте изменить параметры поиска или фильтрации.
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'books-grid' : 'books-list'}>
          {books.map((book) => (
            <BookCard key={book.id} book={book} viewMode={viewMode} />
          ))}
        </div>
      )}

      {/* Кнопки пагинации страниц */}
      {(hasPrev || hasNext) && (
        <div className="pagination">
          <button
            type="button"
            className="btn btn-outline"
            disabled={!hasPrev}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Назад
          </button>
          <span>Страница {page}</span>
          <button
            type="button"
            className="btn btn-outline"
            disabled={!hasNext}
            onClick={() => setPage((p) => p + 1)}
          >
            Вперед →
          </button>
        </div>
      )}
    </div>
  );
}
