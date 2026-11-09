import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Loan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("borrowed_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")),
                ("due_at", models.DateTimeField(verbose_name="Срок возврата (до какой даты)")),
                ("returned_at", models.DateTimeField(blank=True, null=True, verbose_name="Фактическая дата возврата")),
                ("status", models.CharField(choices=[("active", "На руках"), ("returned", "Возвращена"), ("overdue", "Просрочена")], default="active", max_length=20, verbose_name="Статус выдачи")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="loans", to="catalog.book", verbose_name="Книга")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="loans", to=settings.AUTH_USER_MODEL, verbose_name="Читатель")),
            ],
            options={
                "verbose_name": "Выдача книги",
                "verbose_name_plural": "Выдачи книг",
                "db_table": "loans_loan",
                "ordering": ["-borrowed_at"],
            },
        ),
    ]
