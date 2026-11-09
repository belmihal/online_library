# ER-диаграмма и схема базы данных «Онлайн-библиотека книг»

Документ фиксирует структуру реляционной базы данных (8 таблиц: 6 основных сущностей и 2 связующие таблицы M2M).

## 1. Диаграмма сущностей (Mermaid)

```mermaid
erDiagram
    USER ||--o{ REVIEW : "пишет"
    USER ||--o{ LOAN : "берёт"
    BOOK ||--o{ REVIEW : "имеет"
    BOOK ||--o{ LOAN : "выдаётся"
    BOOK ||--o{ BOOK_AUTHORS : "написана"
    BOOK ||--o{ BOOK_GENRES : "относится к"
    AUTHOR ||--o{ BOOK_AUTHORS : "автор"
    GENRE ||--o{ BOOK_GENRES : "включает"

    USER {
        int id PK
        string username UK
        string email UK
        string role "reader | admin"
        bool is_active
    }

    AUTHOR {
        int id PK
        string first_name
        string last_name
        text bio
        date birth_date
    }

    GENRE {
        int id PK
        string name UK
        string slug UK
        text description
    }

    BOOK {
        int id PK
        string title
        string isbn UK
        text description
        int published_year
        string publisher
        int pages
        string language
        string cover_url
        int total_copies
        int available_copies
        decimal avg_rating "Обновляется при добавлении отзыва"
    }

    BOOK_AUTHORS {
        int id PK
        int book_id FK
        int author_id FK
    }

    BOOK_GENRES {
        int id PK
        int book_id FK
        int genre_id FK
    }

    REVIEW {
        int id PK
        int user_id FK
        int book_id FK
        int rating "1..5"
        text comment
        datetime created_at
    }

    LOAN {
        int id PK
        int user_id FK
        int book_id FK
        datetime borrowed_at
        datetime due_at
        datetime returned_at "NULL если на руках"
        string status "active | returned | overdue"
    }
```

## 2. Ограничения целостности
* **Уникальные поля (UNIQUE):**
  * `users_user`: `username`, `email`
  * `catalog_genre`: `name`, `slug`
  * `catalog_book`: `isbn`
  * `reviews_review`: пара `(user_id, book_id)` (один пользователь — один отзыв на книгу).
* **Проверки значений:**
  * `reviews_review.rating`: от `1` до `5`.
  * `catalog_book.available_copies`: от `0` до `total_copies`.
