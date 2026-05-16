from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('rented', 'В аренде'),
        ('reserved', 'Забронирована'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название книги")
    author = models.CharField(max_length=100, verbose_name="Автор")
    category = models.CharField(max_length=100, verbose_name="Категория/Жанр")
    year = models.IntegerField(verbose_name="Год написания")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена аренды/покупки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return f"{self.title} — {self.author}"

class Rental(models.Model):
    DURATION_CHOICES = [
        (14, '2 недели'),
        (30, '1 месяц'),
        (90, '3 месяца'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    rental_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала аренды")
    duration_days = models.IntegerField(choices=DURATION_CHOICES, verbose_name="Срок аренды")
    is_active = models.BooleanField(default=True, verbose_name="Активна ли аренда")

    def get_expiration_date(self):
        return self.rental_date + timedelta(days=self.duration_days)

    def is_expired(self):
        return timezone.now() > self.get_expiration_date()
