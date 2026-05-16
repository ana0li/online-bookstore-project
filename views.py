from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Book, Rental

# --- ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ ---

def book_catalog(request):
    """Каталог книг с многофакторной сортировкой и фильтрацией"""
    books = Book.objects.all()

    # Фильтрация по параметрам из URL-запроса
    category = request.GET.get('category')
    author = request.GET.get('author')
    year = request.GET.get('year')

    if category:
        books = books.filter(category__iexact=category)
    if author:
        books = books.filter(author__iexact=author)
    if year:
        books = books.filter(year=year)

    # Сортировка по кнопкам (например, по году или цене)
    sort_by = request.GET.get('sort', 'title')
    books = books.order_by(sort_by)

    return render(request, 'catalog/book_list.html', {'books': books})

@login_required
def rent_book(request, book_id):
    """Функция покупки/аренды книги на выбранный срок"""
    book = get_object_or_404(Book, id=book_id)
    if book.status == 'available' and request.method == 'POST':
        duration = int(request.POST.get('duration', 14)) # Получаем 14, 30 или 90 дней
        
        # Создаем запись аренды
        Rental.objects.create(user=request.user, book=book, duration_days=duration)
        
        # Меняем статус книги на "В аренде"
        book.status = 'rented'
        book.save()
        return redirect('book_catalog')
    return render(request, 'catalog/rent_confirm.html', {'book': book})


# --- ИНТЕРФЕЙС АДМИНИСТРАТОРА ---

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Панель администратора для управления книгами и ценами"""
    books = Book.objects.all()
    active_rentals = Rental.objects.filter(is_active=True)
    
    return render(request, 'admin/dashboard.html', {
        'books': books,
        'active_rentals': active_rentals
    })

@user_passes_test(is_admin)
def check_and_remind_rentals(request):
    """Автоматическая функция напоминания пользователям об окончании аренды"""
    active_rentals = Rental.objects.filter(is_active=True)
    reminded_count = 0

    for rental in active_rentals:
        # Если до конца аренды осталось меньше 3 дней
        time_left = rental.get_expiration_date() - timezone.now()
        if time_left.days <= 3:
            # Имитация отправки email или системного сообщения пользователю
            print(f"Напоминание: Уважаемый {rental.user.username}, срок аренды книги '{rental.book.title}' истекает!")
            reminded_count += 1

    return render(request, 'admin/remind_success.html', {'count': reminded_count})
