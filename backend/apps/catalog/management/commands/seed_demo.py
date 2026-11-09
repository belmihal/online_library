from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.catalog.models import Author, Book, Genre
from apps.loans.models import Loan
from apps.reviews.models import Review
from apps.reviews.views import recalculate_book_rating
from apps.users.models import User


class Command(BaseCommand):
    help = "Заполняет базу данных демо-данными: админ, читатель, 5 авторов, 5 жанров и 10 книг."

    def handle(self, *args, **options):
        self.stdout.write("Начинаем заполнение базы демонстрационными данными (seed_demo)...")

        admin_user, created_admin = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@library.local",
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
                "email": "reader@library.local",
                "role": User.ROLE_READER,
            },
        )
        if created_reader:
            reader_user.set_password("reader123")
            reader_user.save()
        Token.objects.get_or_create(user=reader_user)

        genres_data = [
            ("Классическая литература", "classic", "Произведения мировой и русской классики."),
            ("Научная фантастика", "sci-fi", "Книги о будущем, космосе и высоких технологиях."),
            ("Детектив и триллер", "detective", "Захватывающие расследования и загадочные преступления."),
            ("Фэнтези и приключения", "fantasy", "Волшебные миры, магия и эпические путешествия."),
            ("IT и программирование", "programming", "Учебники и руководства по разработке ПО и архитектуре."),
        ]
        genres = {}
        for name, slug, desc in genres_data:
            genre_obj, _ = Genre.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": desc},
            )
            genres[slug] = genre_obj

        authors_data = [
            ("Михаил", "Булгаков", date(1891, 5, 15), "Русский писатель, драматург, автор романа «Мастер и Маргарита»."),
            ("Федор", "Достоевский", date(1821, 11, 11), "Классик русской литературы и мировой философии."),
            ("Айзек", "Азимов", date(1920, 1, 2), "Американский писатель-фантаст, популяризатор науки."),
            ("Артур", "Конан Дойл", date(1859, 5, 22), "Английский писатель, создатель сыщика Шерлока Холмса."),
            ("Роберт", "Мартин", date(1952, 12, 5), "Инженер-программист, автор бестселлеров «Чистый код» и «Чистая архитектура»."),
        ]
        authors = {}
        for first_name, last_name, birth_date, bio in authors_data:
            author_obj, _ = Author.objects.update_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={"birth_date": birth_date, "bio": bio},
            )
            authors[last_name] = author_obj

        books_data = [
            {
                "title": "Мастер и Маргарита",
                "isbn": "978-5-17-090630-1",
                "description": "Бессмертный философский и мистический роман о визите Воланда в Москву 1930-х годов.",
                "published_year": 1967,
                "publisher": "АСТ",
                "pages": 480,
                "total_copies": 5,
                "authors": ["Булгаков"],
                "genres": ["classic", "fantasy"],
            },
            {
                "title": "Собачье сердце",
                "isbn": "978-5-17-090630-2",
                "description": "Сатирическая повесть о смелом научном эксперименте профессора Преображенского.",
                "published_year": 1925,
                "publisher": "Азбука",
                "pages": 224,
                "total_copies": 4,
                "authors": ["Булгаков"],
                "genres": ["classic", "sci-fi"],
            },
            {
                "title": "Преступление и наказание",
                "isbn": "978-5-17-090630-3",
                "description": "Глубокий психологический роман о студенте Родионе Раскольникове и нравственном выборе.",
                "published_year": 1866,
                "publisher": "Эксмо",
                "pages": 608,
                "total_copies": 6,
                "authors": ["Достоевский"],
                "genres": ["classic", "detective"],
            },
            {
                "title": "Идиот",
                "isbn": "978-5-17-090630-4",
                "description": "История князя Мышкина — искреннего и благородного человека в сложном обществе.",
                "published_year": 1869,
                "publisher": "Эксмо",
                "pages": 640,
                "total_copies": 3,
                "authors": ["Достоевский"],
                "genres": ["classic"],
            },
            {
                "title": "Основание (Академия)",
                "isbn": "978-5-17-090630-5",
                "description": "Классика космооперы о науке психоистории и спасении знаний Галактической Империи.",
                "published_year": 1951,
                "publisher": "Эксмо",
                "pages": 320,
                "total_copies": 4,
                "authors": ["Азимов"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Я, робот",
                "isbn": "978-5-17-090630-6",
                "description": "Сборник научно-фантастических рассказов, сформулировавший Три закона робототехники.",
                "published_year": 1950,
                "publisher": "АСТ",
                "pages": 352,
                "total_copies": 5,
                "authors": ["Азимов"],
                "genres": ["sci-fi"],
            },
            {
                "title": "Приключения Шерлока Холмса",
                "isbn": "978-5-17-090630-7",
                "description": "Знаменитые дедуктивные расследования сыщика с Бейкер-стрит и доктора Ватсона.",
                "published_year": 1892,
                "publisher": "Азбука",
                "pages": 416,
                "total_copies": 5,
                "authors": ["Конан Дойл"],
                "genres": ["detective", "classic"],
            },
            {
                "title": "Собака Баскервилей",
                "isbn": "978-5-17-090630-8",
                "description": "Готический детектив о проклятии древнего рода Баскервилей на болотах Девоншира.",
                "published_year": 1902,
                "publisher": "Азбука",
                "pages": 288,
                "total_copies": 3,
                "authors": ["Конан Дойл"],
                "genres": ["detective"],
            },
            {
                "title": "Чистый код: создание, анализ и рефакторинг",
                "isbn": "978-5-17-090630-9",
                "description": "Настольная книга каждого разработчика о том, как писать понятный и поддерживаемый код.",
                "published_year": 2008,
                "publisher": "Питер",
                "pages": 464,
                "total_copies": 7,
                "authors": ["Мартин"],
                "genres": ["programming"],
            },
            {
                "title": "Чистая архитектура. Искусство разработки ПО",
                "isbn": "978-5-17-090631-0",
                "description": "Практическое руководство по проектированию надежных и простых программных систем.",
                "published_year": 2017,
                "publisher": "Питер",
                "pages": 352,
                "total_copies": 4,
                "authors": ["Мартин"],
                "genres": ["programming"],
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
                    "total_copies": item["total_copies"],
                    "available_copies": item["total_copies"],
                },
            )
            book_obj.authors.set([authors[last_name] for last_name in item["authors"]])
            book_obj.genres.set([genres[slug] for slug in item["genres"]])
            created_books.append(book_obj)

        if created_books:
            first_book = created_books[0]
            second_book = created_books[8]

            Review.objects.update_or_create(
                user=reader_user,
                book=first_book,
                defaults={
                    "rating": 5,
                    "comment": "Шедевр на все времена! Читается на одном дыхании.",
                },
            )
            recalculate_book_rating(first_book)

            Review.objects.update_or_create(
                user=reader_user,
                book=second_book,
                defaults={
                    "rating": 5,
                    "comment": "Отличная книга, очень помогла при подготовке учебного проекта!",
                },
            )
            recalculate_book_rating(second_book)

            if not Loan.objects.filter(user=reader_user, book=first_book, status=Loan.STATUS_ACTIVE).exists():
                Loan.objects.create(
                    user=reader_user,
                    book=first_book,
                    due_at=timezone.now() + timedelta(days=14),
                    status=Loan.STATUS_ACTIVE,
                )
                first_book.available_copies = max(0, first_book.total_copies - 1)
                first_book.save(update_fields=["available_copies"])

        self.stdout.write(
            self.style.SUCCESS(
                "Готово! Созданы: admin (admin123), reader (reader123), 5 авторов, 5 жанров и 10 книг."
            )
        )
