Архитектурный документ: «Онлайн-библиотека книг»
Версия: 1.0
Назначение: контракт для разработки. Стек фиксирован, изменения только через обновление этого документа.

1. ER-диаграмма
1.1. Сущности (минимум 5 таблиц + 2 m2m)
Таблица	Назначение
users_user	Пользователи (читатели, админы). Расширяем AbstractUser.
catalog_author	Авторы книг.
catalog_genre	Жанры/категории.
catalog_book	Книги.
catalog_book_authors	M2M: книга ↔ автор.
catalog_book_genres	M2M: книга ↔ жанр.
reviews_review	Отзывы и оценки пользователей на книги.
loans_loan	Выдачи/бронирования книг (история «взял/вернул»).
Итого 8 таблиц, из них 2 — явные связующие (m2m). Django может генерировать их автоматически, но в ER фиксируем явно как контракт (на случай добавления полей в through-модель).

1.2. Mermaid
erDiagram
    USER ||--o{ REVIEW : "пишет"
    USER ||--o{ LOAN : "берёт"
    BOOK ||--o{ REVIEW : "имеет"
    BOOK ||--o{ LOAN : "выдаётся"
    BOOK ||--o{ BOOK_AUTHORS : ""
    BOOK ||--o{ BOOK_GENRES : ""
    AUTHOR ||--o{ BOOK_AUTHORS : ""
    GENRE ||--o{ BOOK_GENRES : ""

    USER {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        string role "reader|admin"
        bool is_active
        datetime created_at
    }

    AUTHOR {
        uuid id PK
        string first_name
        string last_name
        text bio
        date birth_date
        string photo_url
        datetime created_at
    }

    GENRE {
        uuid id PK
        string name UK
        string slug UK
        text description
    }

    BOOK {
        uuid id PK
        string title
        string slug UK
        text description
        string isbn UK
        int published_year
        string publisher
        int pages
        string language
        string cover_url
        int total_copies
        int available_copies
        decimal avg_rating "денормализация, обновляется сигналом"
        datetime created_at
        datetime updated_at
    }

    BOOK_AUTHORS {
        uuid id PK
        uuid book_id FK
        uuid author_id FK
    }

    BOOK_GENRES {
        uuid id PK
        uuid book_id FK
        uuid genre_id FK
    }

    REVIEW {
        uuid id PK
        uuid user_id FK
        uuid book_id FK
        int rating "1..5"
        text comment
        datetime created_at
        datetime updated_at
    }

    LOAN {
        uuid id PK
        uuid user_id FK
        uuid book_id FK
        datetime borrowed_at
        datetime due_at
        datetime returned_at "null = ещё не возвращена"
        string status "active|returned|overdue"
    }
1.3. Правила и ограничения
Первичные ключи — UUID (кроме USER, где можно BigAutoField — согласовать отдельно; по умолчанию берём UUID для всего).

BOOK.isbn — UNIQUE, BOOK.slug — UNIQUE, GENRE.name/slug — UNIQUE, USER.username/email — UNIQUE.

Уникальные пары: BOOK_AUTHORS(book_id, author_id), BOOK_GENRES(book_id, genre_id).

Уникальное ограничение: один пользователь — один отзыв на книгу → REVIEW(user_id, book_id) UNIQUE.

REVIEW.rating — CHECK 1..5.

LOAN.returned_at IS NULL ⇒ status IN ('active','overdue').

BOOK.available_copies >= 0 (CHECK), BOOK.available_copies <= BOOK.total_copies (CHECK).

BOOK.avg_rating — денормализованное поле, пересчитывается сигналом post_save/post_delete на REVIEW. Источник истины — таблица REVIEW.

Все FK — ON DELETE:

BOOK_AUTHORS, BOOK_GENRES, REVIEW — CASCADE от BOOK.

LOAN — PROTECT от BOOK (историю нельзя терять).

REVIEW.user_id, LOAN.user_id — CASCADE от USER.

1.4. Индексы (обязательные)
BOOK(title), BOOK(published_year), BOOK(avg_rating).

REVIEW(book_id), REVIEW(user_id).

LOAN(user_id, status), LOAN(book_id, status).

GIN/trigram на BOOK.title и AUTHOR.last_name — для поиска (опционально, отмечаем как «если понадобится»).

2. REST-эндпоинты
Базовый префикс: /api/v1/. Формат — JSON. Авторизация — Authorization: Bearer <access>.

Пагинация: ?page=&page_size= (по умолчанию 20, максимум 100). Формат ответа пагинации:

json
{ "count": 123, "next": "url", "previous": null, "results": [ ... ] }
2.1. Аутентификация (/api/v1/auth/)
Метод	URL	Тело запроса	Ответ (2xx)	Ошибки
POST	/auth/register/	{username, email, password, password_confirm}	201 {id, username, email}	400 (валидация, занят username/email)
POST	/auth/login/	{username, password}	200 {access, refresh}	400, 401
POST	/auth/refresh/	{refresh}	200 {access}	401
POST	/auth/logout/	{refresh}	204	401
GET	/auth/me/	—	200 {id, username, email, role}	401
PATCH	/auth/me/	{email?, first_name?, last_name?}	200 {user}	400, 401
2.2. Авторы (/api/v1/authors/)
Метод	URL	Тело	Ответ	Ошибки
GET	/authors/	—	200 paginated AuthorList	—
POST	/authors/	{first_name, last_name, bio?, birth_date?, photo_url?}	201 AuthorDetail	400, 401, 403 (только admin)
GET	/authors/{id}/	—	200 AuthorDetail	404
PATCH	/authors/{id}/	частичное	200 AuthorDetail	400, 401, 403, 404
DELETE	/authors/{id}/	—	204	401, 403, 404
2.3. Жанры (/api/v1/genres/)
Метод	URL	Тело	Ответ	Ошибки
GET	/genres/	—	200 paginated Genre	—
POST	/genres/	{name, slug, description?}	201 Genre	400, 401, 403
GET	/genres/{id}/	—	200 Genre	404
PATCH	/genres/{id}/	частичное	200 Genre	400, 401, 403, 404
DELETE	/genres/{id}/	—	204	401, 403, 404
2.4. Книги (/api/v1/books/)
Метод	URL	Тело	Ответ	Ошибки
GET	/books/	query: ?search=&author=&genre=&year_min=&year_max=&ordering=&page=	200 paginated BookList	400 (кривой query)
POST	/books/	{title, description, isbn, published_year, publisher, pages, language, cover_url, total_copies, author_ids[], genre_ids[]}	201 BookDetail	400, 401, 403
GET	/books/{id}/	—	200 BookDetail	404
PATCH	/books/{id}/	частичное	200 BookDetail	400, 401, 403, 404
DELETE	/books/{id}/	—	204	401, 403, 404
GET	/books/{id}/reviews/	—	200 paginated Review	404
POST	/books/{id}/reviews/	{rating, comment?}	201 Review	400, 401, 404, 409 (уже есть отзыв)
BookList (краткое):

json
{ "id": "uuid", "title": "…", "cover_url": "…", "published_year": 1967,
  "authors": [{"id":"uuid","full_name":"…"}], "genres": [{"id":"uuid","name":"…"}],
  "avg_rating": 4.5, "available_copies": 3 }
BookDetail — то же + description, isbn, publisher, pages, language, total_copies, created_at, updated_at.

2.5. Отзывы (/api/v1/reviews/)
Метод	URL	Тело	Ответ	Ошибки
GET	/reviews/	query: ?book=&user=	200 paginated Review	—
GET	/reviews/{id}/	—	200 Review	404
PATCH	/reviews/{id}/	{rating?, comment?}	200 Review	400, 401, 403, 404
DELETE	/reviews/{id}/	—	204	401, 403, 404
Правило: PATCH/DELETE — только автор отзыва или admin.

2.6. Выдачи (/api/v1/loans/)
Метод	URL	Тело	Ответ	Ошибки
GET	/loans/	query: ?status=&user= (reader видит только свои)	200 paginated Loan	401
POST	/loans/	{book_id, due_at}	201 Loan	400, 401, 409 (нет доступных копий)
POST	/loans/{id}/return/	—	200 Loan	401, 403, 404, 409 (уже возвращена)
GET	/loans/{id}/	—	200 Loan	401, 403, 404
Loan:

json
{ "id":"uuid","book":{"id":"uuid","title":"…"},"user_id":"uuid",
  "borrowed_at":"…","due_at":"…","returned_at":null,"status":"active" }
2.7. Служебные
Метод	URL	Ответ
GET	/health/	200 {"status":"ok"}
GET	/schema/	200 OpenAPI YAML
GET	/docs/	Swagger UI
2.8. Сводная таблица кодов
200 — успешный GET/PATCH.

201 — создание.

204 — удаление.

400 — валидация.

401 — нет/просрочен токен.

403 — прав недостаточно.

404 — объект не найден.

409 — конфликт состояния (дубль отзыва, нет копий, уже возвращена).

422 — не используется (все ошибки валидации → 400).

500 — внутренняя.

3. Черновик OpenAPI 3.0 (yaml)
yaml
openapi: 3.0.3
info:
  title: Online Library API
  version: 1.0.0
  description: API учебного проекта «Онлайн-библиотека книг»
servers:
  - url: http://localhost:8000/api/v1
    description: Local dev
  - url: https://api.library.example.com/api/v1
    description: Prod

tags:
  - name: auth
  - name: authors
  - name: genres
  - name: books
  - name: reviews
  - name: loans

security:
  - BearerAuth: []

paths:
  /auth/register/:
    post:
      tags: [auth]
      security: []
      summary: Регистрация пользователя
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [username, email, password, password_confirm]
              properties:
                username: { type: string, minLength: 3, maxLength: 150 }
                email: { type: string, format: email }
                password: { type: string, minLength: 8 }
                password_confirm: { type: string, minLength: 8 }
      responses:
        '201':
          description: Создан
          content:
            application/json:
              schema: { $ref: '#/components/schemas/User' }
        '400': { $ref: '#/components/responses/BadRequest' }

  /auth/login/:
    post:
      tags: [auth]
      security: []
      summary: Получение JWT
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [username, password]
              properties:
                username: { type: string }
                password: { type: string }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  access: { type: string }
                  refresh: { type: string }
        '401': { $ref: '#/components/responses/Unauthorized' }

  /auth/refresh/:
    post:
      tags: [auth]
      security: []
      summary: Обновление access-токена
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [refresh]
              properties:
                refresh: { type: string }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  access: { type: string }
        '401': { $ref: '#/components/responses/Unauthorized' }

  /auth/me/:
    get:
      tags: [auth]
      summary: Текущий пользователь
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/User' }
        '401': { $ref: '#/components/responses/Unauthorized' }
    patch:
      tags: [auth]
      summary: Обновить профиль
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email: { type: string, format: email }
                first_name: { type: string }
                last_name: { type: string }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/User' }
        '400': { $ref: '#/components/responses/BadRequest' }

  /authors/:
    get:
      tags: [authors]
      summary: Список авторов
      parameters:
        - { $ref: '#/components/parameters/Page' }
        - { $ref: '#/components/parameters/PageSize' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedAuthors'
    post:
      tags: [authors]
      summary: Создать автора (admin)
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/AuthorInput' }
      responses:
        '201':
          description: Создан
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Author' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '403': { $ref: '#/components/responses/Forbidden' }

  /authors/{id}/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    get:
      tags: [authors]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Author' }
        '404': { $ref: '#/components/responses/NotFound' }
    patch:
      tags: [authors]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/AuthorInput' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Author' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '403': { $ref: '#/components/responses/Forbidden' }
        '404': { $ref: '#/components/responses/NotFound' }
    delete:
      tags: [authors]
      responses:
        '204': { description: Удалено }
        '403': { $ref: '#/components/responses/Forbidden' }
        '404': { $ref: '#/components/responses/NotFound' }

  /genres/:
    get:
      tags: [genres]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedGenres'
    post:
      tags: [genres]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/GenreInput' }
      responses:
        '201':
          description: Создан
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Genre' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '403': { $ref: '#/components/responses/Forbidden' }

  /genres/{id}/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    get:
      tags: [genres]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Genre' }
        '404': { $ref: '#/components/responses/NotFound' }
    patch:
      tags: [genres]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/GenreInput' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Genre' }
    delete:
      tags: [genres]
      responses:
        '204': { description: Удалено }

  /books/:
    get:
      tags: [books]
      summary: Список книг с фильтрами и поиском
      parameters:
        - { $ref: '#/components/parameters/Page' }
        - { $ref: '#/components/parameters/PageSize' }
        - { name: search, in: query, schema: { type: string } }
        - { name: author, in: query, schema: { type: string, format: uuid } }
        - { name: genre, in: query, schema: { type: string, format: uuid } }
        - { name: year_min, in: query, schema: { type: integer } }
        - { name: year_max, in: query, schema: { type: integer } }
        - name: ordering
          in: query
          schema:
            type: string
            enum: [title, -title, published_year, -published_year, avg_rating, -avg_rating]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedBooks'
    post:
      tags: [books]
      summary: Создать книгу (admin)
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/BookInput' }
      responses:
        '201':
          description: Создана
          content:
            application/json:
              schema: { $ref: '#/components/schemas/BookDetail' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '403': { $ref: '#/components/responses/Forbidden' }

  /books/{id}/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    get:
      tags: [books]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/BookDetail' }
        '404': { $ref: '#/components/responses/NotFound' }
    patch:
      tags: [books]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/BookInput' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/BookDetail' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '403': { $ref: '#/components/responses/Forbidden' }
        '404': { $ref: '#/components/responses/NotFound' }
    delete:
      tags: [books]
      responses:
        '204': { description: Удалено }

  /books/{id}/reviews/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    get:
      tags: [books, reviews]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedReviews'
    post:
      tags: [books, reviews]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/ReviewInput' }
      responses:
        '201':
          description: Создан
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Review' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '401': { $ref: '#/components/responses/Unauthorized' }
        '409': { $ref: '#/components/responses/Conflict' }

  /reviews/:
    get:
      tags: [reviews]
      parameters:
        - { name: book, in: query, schema: { type: string, format: uuid } }
        - { name: user, in: query, schema: { type: string, format: uuid } }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedReviews'

  /reviews/{id}/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    get:
      tags: [reviews]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Review' }
    patch:
      tags: [reviews]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/ReviewInput' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Review' }
        '403': { $ref: '#/components/responses/Forbidden' }
    delete:
      tags: [reviews]
      responses:
        '204': { description: Удалено }
        '403': { $ref: '#/components/responses/Forbidden' }

  /loans/:
    get:
      tags: [loans]
      parameters:
        - { name: status, in: query, schema: { type: string, enum: [active, returned, overdue] } }
        - { name: user, in: query, schema: { type: string, format: uuid } }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedLoans'
        '401': { $ref: '#/components/responses/Unauthorized' }
    post:
      tags: [loans]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [book_id, due_at]
              properties:
                book_id: { type: string, format: uuid }
                due_at: { type: string, format: date-time }
      responses:
        '201':
          description: Создана
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Loan' }
        '400': { $ref: '#/components/responses/BadRequest' }
        '409': { $ref: '#/components/responses/Conflict' }

  /loans/{id}/return/:
    parameters:
      - { $ref: '#/components/parameters/IdPath' }
    post:
      tags: [loans]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Loan' }
        '403': { $ref: '#/components/responses/Forbidden' }
        '404': { $ref: '#/components/responses/NotFound' }
        '409': { $ref: '#/components/responses/Conflict' }

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    Page:
      name: page
      in: query
      schema: { type: integer, minimum: 1, default: 1 }
    PageSize:
      name: page_size
      in: query
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
    IdPath:
      name: id
      in: path
      required: true
      schema: { type: string, format: uuid }

  responses:
    BadRequest:
      description: Ошибка валидации
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
    Unauthorized:
      description: Требуется аутентификация
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
    Forbidden:
      description: Недостаточно прав
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
    NotFound:
      description: Не найдено
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
    Conflict:
      description: Конфликт состояния
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

  schemas:
    Error:
      type: object
      properties:
        detail: { type: string }
        errors:
          type: object
          additionalProperties: true

    User:
      type: object
      properties:
        id: { type: string, format: uuid }
        username: { type: string }
        email: { type: string, format: email }
        first_name: { type: string }
        last_name: { type: string }
        role: { type: string, enum: [reader, admin] }

    Author:
      type: object
      properties:
        id: { type: string, format: uuid }
        first_name: { type: string }
        last_name: { type: string }
        full_name: { type: string }
        bio: { type: string, nullable: true }
        birth_date: { type: string, format: date, nullable: true }
        photo_url: { type: string, format: uri, nullable: true }

    AuthorInput:
      type: object
      required: [first_name, last_name]
      properties:
        first_name: { type: string, maxLength: 100 }
        last_name: { type: string, maxLength: 100 }
        bio: { type: string }
        birth_date: { type: string, format: date }
        photo_url: { type: string, format: uri }

    Genre:
      type: object
      properties:
        id: { type: string, format: uuid }
        name: { type: string }
        slug: { type: string }
        description: { type: string, nullable: true }

    GenreInput:
      type: object
      required: [name, slug]
      properties:
        name: { type: string, maxLength: 80 }
        slug: { type: string, maxLength: 80 }
        description: { type: string }

    AuthorShort:
      type: object
      properties:
        id: { type: string, format: uuid }
        full_name: { type: string }

    GenreShort:
      type: object
      properties:
        id: { type: string, format: uuid }
        name: { type: string }

    BookList:
      type: object
      properties:
        id: { type: string, format: uuid }
        title: { type: string }
        cover_url: { type: string, format: uri, nullable: true }
        published_year: { type: integer, nullable: true }
        avg_rating: { type: number, format: float, nullable: true }
        available_copies: { type: integer }
        authors:
          type: array
          items: { $ref: '#/components/schemas/AuthorShort' }
        genres:
          type: array
          items: { $ref: '#/components/schemas/GenreShort' }

    BookDetail:
      allOf:
        - $ref: '#/components/schemas/BookList'
        - type: object
          properties:
            description: { type: string, nullable: true }
            isbn: { type: string, nullable: true }
            publisher: { type: string, nullable: true }
            pages: { type: integer, nullable: true }
            language: { type: string, nullable: true }
            total_copies: { type: integer }
            created_at: { type: string, format: date-time }
            updated_at: { type: string, format: date-time }

    BookInput:
      type: object
      required: [title, total_copies]
      properties:
        title: { type: string, maxLength: 300 }
        description: { type: string }
        isbn: { type: string }
        published_year: { type: integer }
        publisher: { type: string }
        pages: { type: integer, minimum: 1 }
        language: { type: string }
        cover_url: { type: string, format: uri }
        total_copies: { type: integer, minimum: 0 }
        author_ids:
          type: array
          items: { type: string, format: uuid }
        genre_ids:
          type: array
          items: { type: string, format: uuid }

    Review:
      type: object
      properties:
        id: { type: string, format: uuid }
        book: { type: string, format: uuid }
        user: { $ref: '#/components/schemas/User' }
        rating: { type: integer, minimum: 1, maximum: 5 }
        comment: { type: string, nullable: true }
        created_at: { type: string, format: date-time }
        updated_at: { type: string, format: date-time }

    ReviewInput:
      type: object
      required: [rating]
      properties:
        rating: { type: integer, minimum: 1, maximum: 5 }
        comment: { type: string, maxLength: 2000 }

    Loan:
      type: object
      properties:
        id: { type: string, format: uuid }
        book: { $ref: '#/components/schemas/BookList' }
        user_id: { type: string, format: uuid }
        borrowed_at: { type: string, format: date-time }
        due_at: { type: string, format: date-time }
        returned_at: { type: string, format: date-time, nullable: true }
        status: { type: string, enum: [active, returned, overdue] }

    PaginatedAuthors:
      type: object
      properties:
        count: { type: integer }
        next: { type: string, nullable: true }
        previous: { type: string, nullable: true }
        results:
          type: array
          items: { $ref: '#/components/schemas/Author' }

    PaginatedGenres:
      type: object
      properties:
        count: { type: integer }
        next: { type: string, nullable: true }
        previous: { type: string, nullable: true }
        results:
          type: array
          items: { $ref: '#/components/schemas/Genre' }

    PaginatedBooks:
      type: object
      properties:
        count: { type: integer }
        next: { type: string, nullable: true }
        previous: { type: string, nullable: true }
        results:
          type: array
          items: { $ref: '#/components/schemas/BookList' }

    PaginatedReviews:
      type: object
      properties:
        count: { type: integer }
        next: { type: string, nullable: true }
        previous: { type: string, nullable: true }
        results:
          type: array
          items: { $ref: '#/components/schemas/Review' }

    PaginatedLoans:
      type: object
      properties:
        count: { type: integer }
        next: { type: string, nullable: true }
        previous: { type: string, nullable: true }
        results:
          type: array
          items: { $ref: '#/components/schemas/Loan' }
Примечание: финальный schema.yaml генерируется drf-spectacular и должен быть закоммичен в /docs/openapi.yaml. Этот черновик — источник истины по форме и кодам.

4. Структура репозитория
text
online-library/
├── README.md
├── docker-compose.yml
├── .env.example
├── .editorconfig
├── .gitignore
├── Makefile
├── docs/
│   ├── ARCHITECTURE.md          # этот файл
│   ├── openapi.yaml             # экспорт drf-spectacular
│   ├── er-diagram.md│   └── adr/
│       ├── 0001-stack.md
│       └── 0002-auth-jwt.md
│
├── backend/
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── manage.py
│   ├── pytest.ini
│   ├── .coveragerc
│   ├── config/                  # django project
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── permissions.py
│   │   │   ├── admin.py
│   │   │   └── tests/
│   │   ├── catalog/             # authors, genres, books
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── filters.py
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── tests/
│   │   ├── reviews/
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── signals.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   └── loans/
│   │       ├── migrations/
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── services.py
│   │       ├── urls.py
│   │       └── tests/
│   ├── common/
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── exceptions.py
│   │   └── mixins.py
│   └── conftest.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── .eslintrc.cjs
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router/
│       │   └── index.tsx
│       ├── api/
│       │   ├── client.ts        # fetch-обёртка + JWT
│       │   ├── auth.ts
│       │   ├── books.ts
│       │   ├── authors.ts
│       │   ├── genres.ts
│       │   ├── reviews.ts
│       │   ├── loans.ts
│       │   └── types.ts         # из openapi (руками/генерация)
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useBooks.ts      # TanStack Query
│       │   └── useDebounce.ts
│       ├── components/
│       │   ├── layout/
│       │   ├── book/
│       │   ├── forms/
│       │   └── ui/
│       ├── pages/
│       │   ├── CatalogPage.tsx
│       │   ├── BookPage.tsx
│       │   ├── LoginPage.tsx
│       │   ├── RegisterPage.tsx
│       │   ├── ProfilePage.tsx
│       │   ├── AdminBooksPage.tsx
│       │   └── NotFoundPage.tsx
│       ├── store/
│       │   └── auth.ts
│       ├── styles/
│       └── test/
│           └── setup.ts
│
└── infra/
    ├── docker/
    │   ├── backend.Dockerfile
    │   ├── frontend.Dockerfile
    │   └── nginx.conf
    ├── env/
    │   ├── backend.env.example
    │   └── frontend.env.example
    └── scripts/
        ├── entrypoint-backend.sh
        ├── entrypoint-frontend.sh
        └── wait-for-db.sh
5. Страницы и формы фронта
5.1. Страницы (7)
#	Маршрут	Название	Что показывает
1	/	Каталог книг	Плитка (grid) карточек книг, поиск, фильтры по жанру/автору/году, сортировка, пагинация. TanStack Query.
2	/books/:id	Карточка книги	Детали, авторы, жанры, средний рейтинг, список отзывов, форма отзыва/оценки, кнопка «Взять книгу».
3	/login	Вход	Форма логина.
4	/register	Регистрация	Форма регистрации.
5	/profile	Личный кабинет	Список «Мои книги» (активные/просроченные/возвращённые), список «Мои отзывы».
6	/admin/books	Админ-каталог	Таблица книг с CRUD-кнопками (только admin).
7	*	404	Страница «не найдено».
5.2. Формы (5)
LoginForm — username, password → POST /auth/login/. Ошибки 400/401.

RegisterForm — username, email, password, password_confirm → POST /auth/register/. Клиентская валидация совпадения паролей.

ReviewForm — rating (1–5), comment → POST /books/{id}/reviews/. Обработка 409 «уже есть отзыв».

BookForm (admin) — все поля книги + мультиселекты авторов и жанров → POST/PATCH /books/.

LoanForm — book_id, due_at → POST /loans/. Используется на странице книги (кнопка «Взять»).

5.3. Где список / плитка
Плитка (grid/cards): Каталог (/), «Похожие книги» на странице книги, «Мои книги» в профиле (можно плиткой).

Список (list/table): Отзывы на странице книги, отзывы в профиле, админ-таблица книг, список выдач в профиле.

Обязательное состояние для каждой выборки: loading / empty / error + кнопка «Повторить» (единый компонент AsyncBoundary).

6. Definition of Done
6.1. Функциональность
□ Все эндпоинты из раздела 2 реализованы и соответствуют контракту OpenAPI.
□ Реализованы CRUD: users (регистрация/логин/профиль), authors, genres, books, reviews, loans.
□ Работает M2M: книга ↔ авторы, книга ↔ жанры (создание/редактирование через API).
□ Работает поиск и фильтрация книг (search, author, genre, year_min/max, ordering).
□ Работают отзывы с рейтингом; avg_rating книги пересчитывается.
□ Работают выдачи: взять книгу (уменьшает available_copies), вернуть (увеличивает), статус overdue вычисляется.
□ Роли: reader видит только свои loans/reviews в личных разделах; admin — управляет каталогом.
6.2. Бэкенд
□ Django 5 + DRF, PostgreSQL.
□ JWT через djangorestframework-simplejwt (access+refresh).
□ Валидация на уровне сериализаторов и БД (constraints).
□ Миграции без ручных правок; python manage.py makemigrations --check в CI.
□ drf-spectacular генерирует /schema/ без ошибок; openapi.yaml закоммичен.
□ pytest-django: покрытие критичных модулей (auth, books, loans, reviews) ≥ 80 %.
□ pytest зелёный локально и в CI.
□ Логирование: 5xx логируются с request_id; секреты не попадают в логи.
6.3. Фронтенд
□ React 18 + Vite + TS (strict: true), React Router, TanStack Query.
□ Все 7 страниц из раздела 5.1 реализованы.
□ Все 5 форм из 5.2 реализованы с валидацией и обработкой ошибок API.
□ Каждая выборка имеет состояния loading/empty/error.
□ JWT: access в памяти + refresh в httpOnly/localStorage (зафиксировать в ADR), авто-refresh, logout.
□ Единый API-клиент с обработкой 401/403/404/409.
□ Vitest + RTL: тесты на формы, карточку книги, каталог (сортировка/фильтр), обработку 409.
□ tsc --noEmit, eslint, vitest run — зелёные.
6.4. Инфра и запуск
□ docker-compose up поднимает backend, frontend, postgres без ручных шагов.
□ Backend ждёт готовности БД (wait-for-db.sh).
□ .env.example покрывает все переменные (DB, SECRET_KEY, CORS, JWT TTL, VITE_API_URL).
□ Миграции применяются на старте backend-контейнера.
□ Есть сид-команда seed_demo (10+ книг, 5+ авторов, 5+ жанров, 1 admin, 1 reader).
□ README описывает: как поднять, как залить сиды, где docs, где тесты.
6.5. Качество и процесс
□ CI (GitHub Actions / аналог): lint + tests backend, lint + typecheck + tests frontend, сборка docker-образов.
□ Conventional Commits; PR-шаблон; правило «одна фича — один PR».
□ docs/ARCHITECTURE.md (этот файл) и docs/openapi.yaml актуальны; изменения API — через PR в docs.
□ Нет закоммиченных секретов; .env в .gitignore.
□ Демо-сценарий из README проходит от docker-compose up до «взял книгу, оставил отзыв» без ошибок в консоли.
6.6. Не входит в DoD (осознанно вне скоупа)
Загрузка файлов (обложки — только URL).

Реальные напоминания по email об overdue.

Полнотекстовый поиск (Postgres FTS) — опционально, вынести в отдельную итерацию.

i18n/мультиязычность интерфейса.

Конец документа. Любое изменение контракта (поля, коды, URL, схема БД) — только через PR в docs/ARCHITECTURE.md + регенерацию docs/openapi.yaml.