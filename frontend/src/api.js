/**
 * Простой модуль для отправки HTTP-запросов к Django-бэкенду LitHub (src/api.js).
 * Использует стандартный браузерный fetch() и хранит токен в localStorage.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

/**
 * Формирует заголовки запроса. Если в localStorage сохранен токен,
 * автоматически добавляет заголовок Authorization: Token <ключ>.
 */
export function getAuthHeaders(isJson = true) {
  const headers = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }

  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }
  return headers;
}

/**
 * Универсальный обработчик ответа сервера.
 * Извлекает понятный текст ошибки на русском языке при неуспешном HTTP-статусе.
 */
export async function handleResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let errorMessage = data.detail || data.non_field_errors?.[0] || '';

    if (!errorMessage && typeof data === 'object' && data !== null) {
      const firstKey = Object.keys(data)[0];
      if (firstKey) {
        const val = data[firstKey];
        errorMessage = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`;
      }
    }

    throw new Error(errorMessage || `Ошибка сервера (код ${response.status})`);
  }

  return data;
}

/**
 * Обертка над fetch() для JSON-запросов (GET, POST, PATCH, DELETE).
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(true),
      ...(options.headers || {}),
    },
  });
  return handleResponse(response);
}

/**
 * Загрузка CSV-файла (multipart/form-data) для админ-панели POST /api/v1/books/import-csv/
 */
export async function uploadBooksCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/books/import-csv/`, {
    method: 'POST',
    headers: getAuthHeaders(false),
    body: formData,
  });

  return handleResponse(response);
}
