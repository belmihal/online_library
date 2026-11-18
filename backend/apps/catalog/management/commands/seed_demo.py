"""
Команда для заполнения базы данных цифровой онлайн-библиотеки «LitHub»:
    python manage.py seed_demo

Создает:
- 2 пользователей:
  1) admin  (email: admin@lithub.local, пароль: admin123, роль: admin)
  2) reader (email: reader@lithub.local, пароль: reader123, роль: reader)
- 8 жанров литературы
- 14 известных авторов
- 32 разнообразные цифровые книги с привязкой к авторам и жанрам (M2M)
- 3 отзыва от читателя reader с пересчетом среднего рейтинга (avg_rating)
- 3 книги на личной полке (ShelfItem) пользователя reader.
"""
from datetime import date
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from apps.catalog.models import Author, Book, Genre
from apps.reviews.models import Review
from apps.reviews.views import recalculate_book_rating
from apps.shelf.models import ShelfItem
from apps.users.models import User


class Command(BaseCommand):
    help = "Заполняет базу данных LitHub: админ, читатель, 8 жанров, 14 авторов и 32 книги."

    def handle(self, *args, **options):
        self.stdout.write("Заполняем базу данных цифровой библиотеки LitHub (seed_demo)...")

        # 1. Создаем администратора и читателя LitHub
        admin_user, created_admin = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@lithub.local",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created_admin:
            admin_user.set_password("admin123")
            admin_user.save()
        Token.objects.get_or_create(user=admin_user)

        reader_user, created_reader = User.objects.get_or_create(
            username="reader",
            defaults={
                "email": "reader@lithub.local",
                "role": User.ROLE_READER,
            },
        )
        if created_reader:
            reader_user.set_password("reader123")
            reader_user.save()
        Token.objects.get_or_create(user=reader_user)

        # 2. Создаем 8 жанров
        genres_data = [
            ("Классическая литература", "classic", "Шедевры мировой и отечественной классики."),
            ("Научная фантастика", "sci-fi", "Космос, будущее человечества, робототехника и научные открытия."),
            ("Детектив и триллер", "detective", "Запутанные расследования, тайны и психологические триллеры."),
            ("Фэнтези и мистика", "fantasy", "Магические вселенные, легенды и мистические истории."),
            ("IT и программирование", "programming", "Архитектура ПО, алгоритмы, чистый код и современные технологии."),
            ("Антиутопия", "dystopia", "Романы-предупреждения о тоталитарном обществе и будущем цивилизации."),
            ("Психология и саморазвитие", "psychology", "Книги о мышлении, привычках, продуктивности и эмоциональном интеллекте."),
            ("Историческая проза", "history", "Масштабные романы о великих эпохах и судьбах людей."),
        ]
        genres = {}
        for name, slug, desc in genres_data:
            genre_obj, _ = Genre.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": desc},
            )
            genres[slug] = genre_obj

        # 3. Создаем 14 авторов
        authors_data = [
            ("Михаил", "Булгаков", date(1891, 5, 15), "Русский писатель и драматург, автор романа «Мастер и Маргарита»."),
            ("Федор", "Достоевский", date(1821, 11, 11), "Великий русский писатель, мыслитель и философ."),
            ("Лев", "Толстой", date(1828, 9, 9), "Классик мировой литературы, автор романов-эпопей «Война и мир» и «Анна Каренина»."),
            ("Антон", "Чехов", date(1860, 1, 29), "Мастер короткого рассказа и мировой драматургии."),
            ("Айзек", "Азимов", date(1920, 1, 2), "Писатель-фантаст, создатель цикла «Основание» и Трех законов робототехники."),
            ("Рэй", "Брэдбери", date(1920, 8, 22), "Американский фантаст, автор «451 градус по Фаренгейту» и «Марсианских хроник»."),
            ("Аркадий и Борис", "Стругацкие", date(1925, 8, 28), "Классики отечественной научной и социальной фантастики."),
            ("Джордж", "Оруэлл", date(1903, 6, 25), "Британский писатель и публицист, автор знаменитых антиутопий."),
            ("Артур", "Конан Дойл", date(1859, 5, 22), "Создатель легендарного сыщика Шерлока Холмса."),
            ("Агата", "Кристи", date(1890, 9, 15), "Королева классического английского детектива."),
            ("Роберт", "Мартин", date(1952, 12, 5), "Инженер-программист и автор бестселлеров «Чистый код» и «Чистая архитектура»."),
            ("Мартин", "Фаулер", date(1963, 12, 18), "Архитектор ПО, специалист по рефакторингу и корпоративным системам."),
            ("Даниэль", "Канеман", date(1934, 3, 5), "Нобелевский лауреат, исследователь когнитивных искажений и принятия решений."),
            ("Эрих Мария", "Ремарк", date(1898, 6, 22), "Немецкий писатель, автор пронзительных романов о человечности и дружбе."),
        ]
        authors = {}
        for first_name, last_name, birth_date, bio in authors_data:
            author_obj, _ = Author.objects.update_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={"birth_date": birth_date, "bio": bio},
            )
            authors[last_name] = author_obj

        # 4. Создаем 32 книги
        books_data = [
            {
                "title": "Мастер и Маргарита",
                "isbn": "978-5-17-100001-1",
                "description": "Философский и мистический роман о визите Воланда в Москву 1930-х годов, любви и творчестве.",
                "published_year": 1967,
                "publisher": "АСТ",
                "pages": 480,
                "authors": ["Булгаков"],
                "genres": ["classic", "fantasy"],
            },
            {
                "title": "Собачье сердце",
                "isbn": "978-5-17-100002-8",
                "description": "Остроумная сатирическая повесть о смелом научном эксперименте профессора Преображенского.",
                "published_year": 1925,
                "publisher": "Азбука",
                "pages": 224,
                "authors": ["Булгаков"],
                "genres": ["classic", "sci-fi"],
            },
            {
                "title": "Белая гвардия",
                "isbn": "978-5-17-100003-5",
                "description": "Роман о судьбе интеллигентной семьи Турбиных в водовороте исторических событий 1918 года.",
                "published_year": 1925,
                "publisher": "АСТ",
                "pages": 384,
                "authors": ["Булгаков"],
                "genres": ["classic", "history"],
            },
            {
                "title": "Преступление и наказание",
                "isbn": "978-5-17-100004-2",
                "description": "Психологический роман о студенте Родионе Раскольникове, теории сверхчеловека и искуплении.",
                "published_year": 1866,
                "publisher": "Эксмо",
                "pages": 608,
                "authors": ["Достоевский"],
                "genres": ["classic", "detective"],
            },
            {
                "title": "Идиот",
                "isbn": "978-5-17-100005-9",
                "description": "Трагическая история искреннего и сострадательного князя Мышкина в петербургском обществе.",
                "published_year": 1869,
                "publisher": "Эксмо",
                "pages": 640,
                "authors": ["Достоевский"],
                "genres": ["classic"],
            },
            {
                "title": "Братья Карамазовы",
                "isbn": "978-5-17-100006-6",
                "description": "Итоговый философско-детективный роман Достоевского о вере, свободе воли и семейной драме.",
                "published_year": 1880,
                "publisher": "Азбука",
                "pages": 832,
                "authors": ["Достоевский"],
                "genres": ["classic", "detective"],
            },
            {
                "title": "Война и мир",
                "isbn": "978-5-17-100007-3",
                "description": "Монументальный роман-эпопея о судьбах русского общества в эпоху наполеоновских войн.",
                "published_year": 1869,
                "publisher": "АСТ",
                "pages": 1300,
                "authors": ["Толстой"],
                "genres": ["classic", "history"],
            },
            {
                "title": "Анна Каренина",
                "isbn": "978-5-17-100008-0",
                "description": "Глубокая история о страсти, семейном долге и поиске смысла жизни в России XIX века.",
                "published_year": 1877,
                "publisher": "Азбука",
                "pages": 864,
                "authors": ["Толстой"],
                "genres": ["classic"],
            },
            {
                "title": "Вишневый сад",
                "isbn": "978-5-17-100009-7",
                "description": "Знаменитая лирическая пьеса о прощании с прошлым и наступлении новой эпохи.",
                "published_year": 1904,
                "publisher": "Эксмо",
                "pages": 192,
                "authors": ["Чехов"],
                "genres": ["classic"],
            },
            {
                "title": "Палата № 6",
                "isbn": "978-5-17-100010-3",
                "description": "Философская повесть о враче Рагине, равнодушии и границах человеческого разума.",
                "published_year": 1892,
                "publisher": "Азбука",
                "pages": 256,
                "authors": ["Чехов"],
                "genres": ["classic", "psychology"],
            },
            {
                "title": "Основание (Академия)",
                "isbn": "978-5-17-100011-0",
                "description": "Легендарная космоопера о науке психоистории и сохранении знаний гибнущей Галактической Империи.",
                "published_year": 1951,
                "publisher": "Эксмо",
                "pages": 320,
                "authors": ["Азимов"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Я, робот",
                "isbn": "978-5-17-100012-7",
                "description": "Цикл рассказов об этике искусственного интеллекта и Трех законах робототехники.",
                "published_year": 1950,
                "publisher": "АСТ",
                "pages": 352,
                "authors": ["Азимов"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Конец Вечности",
                "isbn": "978-5-17-100013-4",
                "description": "Захватывающий роман о путешествиях во времени и организации, корректирующей историю человечества.",
                "published_year": 1955,
                "publisher": "Эксмо",
                "pages": 288,
                "authors": ["Азимов"],
                "genres": ["sci-fi"],
            },
            {
                "title": "451 градус по Фаренгейту",
                "isbn": "978-5-17-100014-1",
                "description": "Культовая антиутопия о мире, где книги запрещены и подлежат сожжению пожарными.",
                "published_year": 1953,
                "publisher": "Эксмо",
                "pages": 256,
                "authors": ["Брэдбери"],
                "genres": ["dystopia", "sci-fi"],
            },
            {
                "title": "Марсианские хроники",
                "isbn": "978-5-17-100015-8",
                "description": "Поэтичная история освоения Красной планеты и встречи двух цивилизаций.",
                "published_year": 1950,
                "publisher": "Эксмо",
                "pages": 352,
                "authors": ["Брэдбери"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Вино из одуванчиков",
                "isbn": "978-5-17-100016-5",
                "description": "Теплая автобиографическая повесть о лете, детстве и радости каждого прожитого дня.",
                "published_year": 1957,
                "publisher": "Эксмо",
                "pages": 384,
                "authors": ["Брэдбери"],
                "genres": ["classic"],
            },
            {
                "title": "Пикник на обочине",
                "isbn": "978-5-17-100017-2",
                "description": "Философская фантастика о таинственной Зоне Посещения, артефактах и сталкере Рэде Шухарте.",
                "published_year": 1972,
                "publisher": "АСТ",
                "pages": 256,
                "authors": ["Стругацкие"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Понедельник начинается в субботу",
                "isbn": "978-5-17-100018-9",
                "description": "Искрометная фантастическая сказка о буднях НИИЧАВО и молодых ученых-энтузиастах.",
                "published_year": 1965,
                "publisher": "АСТ",
                "pages": 320,
                "authors": ["Стругацкие"],
                "genres": ["fantasy", "sci-fi"],
            },
            {
                "title": "Трудно быть богом",
                "isbn": "978-5-17-100019-6",
                "description": "Роман о прогрессоре доне Румате на планете, застрявшей в мрачном Средневековье.",
                "published_year": 1964,
                "publisher": "АСТ",
                "pages": 288,
                "authors": ["Стругацкие"],
                "genres": ["sci-fi", "history"],
            },
            {
                "title": "1984",
                "isbn": "978-5-17-100020-2",
                "description": "Главный роман-антиутопия XX века о Большом Брате, новоязе и борьбе за свободу мысли.",
                "published_year": 1949,
                "publisher": "АСТ",
                "pages": 320,
                "authors": ["Оруэлл"],
                "genres": ["dystopia", "classic"],
            },
            {
                "title": "Скотный двор",
                "isbn": "978-5-17-100021-9",
                "description": "Острая политическая притча о перерождении революционных идеалов.",
                "published_year": 1945,
                "publisher": "АСТ",
                "pages": 160,
                "authors": ["Оруэлл"],
                "genres": ["dystopia", "classic"],
            },
            {
                "title": "Приключения Шерлока Холмса",
                "isbn": "978-5-17-100022-6",
                "description": "Классический сборник детективных историй о дедуктивном методе сыщика с Бейкер-стрит.",
                "published_year": 1892,
                "publisher": "Азбука",
                "pages": 416,
                "authors": ["Конан Дойл"],
                "genres": ["detective", "classic"],
            },
            {
                "title": "Собака Баскервилей",
                "isbn": "978-5-17-100023-3",
                "description": "Готический детектив о загадочном проклятии древнего рода на торфяных болотах Девоншира.",
                "published_year": 1902,
                "publisher": "Азбука",
                "pages": 288,
                "authors": ["Конан Дойл"],
                "genres": ["detective"],
            },
            {
                "title": "Убийство в Восточном экспрессе",
                "isbn": "978-5-17-100024-0",
                "description": "Знаменитое расследование Эркюля Пуаро в застрявшем в снегах роскошном поезде.",
                "published_year": 1934,
                "publisher": "Эксмо",
                "pages": 320,
                "authors": ["Кристи"],
                "genres": ["detective"],
            },
            {
                "title": "Десять негритят",
                "isbn": "978-5-17-100025-7",
                "description": "Эталонный герметичный детектив-триллер о десяти незнакомцах на уединенном острове.",
                "published_year": 1939,
                "publisher": "Эксмо",
                "pages": 288,
                "authors": ["Кристи"],
                "genres": ["detective"],
            },
            {
                "title": "Чистый код: создание, анализ и рефакторинг",
                "isbn": "978-5-17-100026-4",
                "description": "Практическое руководство по написанию читаемого, простого и надежного программного кода.",
                "published_year": 2008,
                "publisher": "Питер",
                "pages": 464,
                "authors": ["Мартин"],
                "genres": ["programming"],
            },
            {
                "title": "Чистая архитектура. Искусство разработки ПО",
                "isbn": "978-5-17-100027-1",
                "description": "Фундаментальные принципы проектирования модульных и поддерживаемых веб-приложений.",
                "published_year": 2017,
                "publisher": "Питер",
                "pages": 352,
                "authors": ["Мартин"],
                "genres": ["programming"],
            },
            {
                "title": "Идеальный программист",
                "isbn": "978-5-17-100028-8",
                "description": "Книга о профессиональной этике, оценке сроков, тестировании и мастерстве разработчика.",
                "published_year": 2011,
                "publisher": "Питер",
                "pages": 224,
                "authors": ["Мартин"],
                "genres": ["programming", "psychology"],
            },
            {
                "title": "Рефакторинг. Улучшение проекта существующего кода",
                "isbn": "978-5-17-100029-5",
                "description": "Классический каталог приемов безопасного улучшения структуры кода без изменения его поведения.",
                "published_year": 2018,
                "publisher": "Питер",
                "pages": 448,
                "authors": ["Фаулер"],
                "genres": ["programming"],
            },
            {
                "title": "Шаблоны корпоративных приложений",
                "isbn": "978-5-17-100030-1",
                "description": "Справочник архитектурных паттернов для построения серверных приложений и работы с БД.",
                "published_year": 2002,
                "publisher": "Вильямс",
                "pages": 544,
                "authors": ["Фаулер"],
                "genres": ["programming"],
            },
            {
                "title": "Думай медленно… решай быстро",
                "isbn": "978-5-17-100031-8",
                "description": "Бестселлер о двух системах мышления, когнитивных ловушках и принятии рациональных решений.",
                "published_year": 2011,
                "publisher": "АСТ",
                "pages": 656,
                "authors": ["Канеман"],
                "genres": ["psychology"],
            },
            {
                "title": "Три товарища",
                "isbn": "978-5-17-100032-5",
                "description": "Трогательный роман о настоящей дружбе, любви и стойкости в послевоенной Германии.",
                "published_year": 1936,
                "publisher": "АСТ",
                "pages": 480,
                "authors": ["Ремарк"],
                "genres": ["classic", "history"],
            },
        ]

        created_books = []
        for item in books_data:
            book_obj, _ = Book.objects.update_or_create(
                isbn=item["isbn"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "published_year": item["published_year"],
                    "publisher": item["publisher"],
                    "pages": item["pages"],
                    "language": "Русский",
                },
            )
            book_obj.authors.set([authors[last_name] for last_name in item["authors"]])
            book_obj.genres.set([genres[slug] for slug in item["genres"]])
            created_books.append(book_obj)

        # 5. Добавляем 3 демонстрационных отзыва от reader и пересчитываем avg_rating
        demo_reviews = [
            (created_books[0], 5, "Бессмертный шедевр! Перечитываю каждый год с огромным удовольствием."),
            (created_books[25], 5, "Лучшая книга для разработчиков — помогает писать понятный и чистый код."),
            (created_books[13], 4, "Сильная и актуальная книга о ценности литературы и свободного мышления."),
        ]
        for book_obj, rating, comment in demo_reviews:
            Review.objects.update_or_create(
                user=reader_user,
                book=book_obj,
                defaults={"rating": rating, "comment": comment},
            )
            recalculate_book_rating(book_obj)

        # 6. Добавляем 3 книги на личную книжную полку (ShelfItem) пользователя reader
        for book_obj in (created_books[0], created_books[10], created_books[25]):
            ShelfItem.objects.get_or_create(user=reader_user, book=book_obj)

        self.stdout.write(
            self.style.SUCCESS(
                "Готово! База LitHub заполнена: admin (admin123), reader (reader123), "
                "8 жанров, 14 авторов, 32 книги, 3 отзыва и 3 книги на полке."
            )
        )
