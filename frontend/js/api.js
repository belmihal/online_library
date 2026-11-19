/**
 * Модуль запросов к REST API цифровой библиотеки LitHub (js/api.js).
 * Работает напрямую в браузере без сборщиков.
 * Токен авторизации читается из localStorage ('token').
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// 8 благородных книжных палитр для стилизованных обложек с корешком
const COVER_PALETTES = [
  'linear-gradient(135deg, #431407 0%, #9a3412 55%, #ea580c 100%)',
  'linear-gradient(135deg, #1e1b4b 0%, #3730a3 60%, #4f46e5 100%)',
  'linear-gradient(135deg, #064e3b 0%, #047857 60%, #10b981 100%)',
  'linear-gradient(135deg, #4c0519 0%, #881337 60%, #be123c 100%)',
  'linear-gradient(135deg, #3b0764 0%, #6b21a8 60%, #9333ea 100%)',
  'linear-gradient(135deg, #1c1917 0%, #44403c 60%, #78716c 100%)',
  'linear-gradient(135deg, #451a03 0%, #78350f 60%, #b45309 100%)',
  'linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #0284c7 100%)',
];

/**
 * Подбирает наглядную иконку для категории (жанра) по её slug или названию
 */
function getGenreIcon(genre) {
  const slug = String((genre && genre.slug) || '').toLowerCase();
  const name = String((genre && genre.name) || '').toLowerCase();

  const iconBySlug = {
    dystopia: '👁️',
    scifi: '👽',
    'sci-fi': '👽',
    fantasy: '🐉',
    classic: '🏛️',
    classics: '🏛️',
    psychology: '🧠',
    'self-development': '🚀',
    children: '👶',
    detective: '🕵️',
    mystery: '🕵️',
    history: '📜',
    science: '🔬',
    programming: '💻',
    romance: '💛',
    business: '💼',
    adventure: '🧭',
  };

  if (iconBySlug[slug]) return iconBySlug[slug];
  if (name.includes('антиутоп')) return '👁️';
  if (name.includes('фантаст')) return '👽';
  if (name.includes('фэнтези')) return '🐉';
  if (name.includes('классик')) return '🏛️';
  if (name.includes('психолог')) return '🧠';
  if (name.includes('саморазвит')) return '🚀';
  if (name.includes('дет')) return '👶';
  if (name.includes('детектив')) return '🕵️';
  if (name.includes('истор')) return '📜';
  if (name.includes('программ') || name.includes('it')) return '💻';
  return '📚';
}

/**
 * Возвращает строку авторов книги
 */
function formatBookAuthors(book) {
  if (book && Array.isArray(book.authors) && book.authors.length > 0) {
    return book.authors
      .map(function (a) {
        return a.full_name || a.first_name + ' ' + a.last_name;
      })
      .join(', ');
  }
  return 'Автор не указан';
}

/**
 * Возвращает текущего сохраненного пользователя из localStorage (или null)
 */
function getCurrentUser() {
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * Формирует HTTP-заголовки с токеном Authorization: Token <ключ>
 */
function getAuthHeaders(isJson) {
  const headers = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = 'Token ' + token;
  }
  return headers;
}

/**
 * Разбирает ответ сервера и выбрасывает понятную ошибку на русском языке при сбое
 */
async function handleResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    let errorMessage = data.detail || (data.non_field_errors && data.non_field_errors[0]) || '';

    if (!errorMessage && typeof data === 'object' && data !== null) {
      const keys = Object.keys(data);
      if (keys.length > 0) {
        const firstKey = keys[0];
        const val = data[firstKey];
        errorMessage = Array.isArray(val) ? firstKey + ': ' + val[0] : firstKey + ': ' + val;
      }
    }

    throw new Error(errorMessage || 'Ошибка сервера (код ' + response.status + ')');
  }

  return data;
}

/**
 * Универсальная функция для JSON-запросов (GET, POST, PATCH, DELETE)
 */
async function apiFetch(endpoint, options) {
  const opts = options || {};
  const response = await fetch(API_BASE_URL + endpoint, {
    ...opts,
    headers: {
      ...getAuthHeaders(true),
      ...(opts.headers || {}),
    },
  });
  return handleResponse(response);
}

/**
 * Загрузка CSV-файла для импорта книг в админ-панели (POST /api/v1/books/import-csv/)
 */
async function uploadBooksCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(API_BASE_URL + '/books/import-csv/', {
    method: 'POST',
    headers: getAuthHeaders(false),
    body: formData,
  });

  return handleResponse(response);
}
