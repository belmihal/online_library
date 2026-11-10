import React from 'react';
import { Link, useParams } from 'react-router-dom';

// Временная заглушка для Шага 1 (полный код страницы книги с отзывами и выдачей будет добавлен на Шаге 2)
export default function BookPage() {
  const { id } = useParams();
  return (
    <div className="card">
      <h1 className="page-title">Страница книги #{id}</h1>
      <p>Полный функционал деталей книги, выдачи и отзывов подключается на Шаге 2.</p>
      <p style={{ marginTop: 12 }}>
        <Link to="/" className="btn btn-outline">← Вернуться в каталог</Link>
      </p>
    </div>
  );
}
