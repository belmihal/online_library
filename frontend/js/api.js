/**
 * Модуль запросов к REST API цифровой библиотеки LitHub (js/api.js).
 * Работает напрямую в браузере без сборщиков.
 * Токен авторизации читается из localStorage ('token').
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

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
