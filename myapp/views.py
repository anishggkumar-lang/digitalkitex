from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils.http import url_has_allowed_host_and_scheme
from decimal import Decimal
from django.db.models import Sum, Q
from .models import Table, MenuItem, Order, OrderItem
import datetime

def home_view(request):
    # Give a new installation one table so a customer can try the ordering flow.
    Table.objects.get_or_create(number=1)
    tables = Table.objects.all().order_by('number')
    today = datetime.date.today()
    total_sales = Order.objects.filter(status='completed', created_at__date=today).count()
    popular_items = OrderItem.objects.filter(order__status='completed').values('menu_item__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]
    return render(request, 'home.html', {'tables': tables, 'total_sales_count': total_sales, 'popular_items': popular_items})

@login_required(login_url='login')
def menu(request, table_number):
    table = get_object_or_404(Table, number=table_number)
    # Ensure the requested starter menu is available on a fresh install.
    starter_items = (
        ('Porrata', Decimal('20.00')),
        ('Dosa', Decimal('50.00')),
        ('Idli', Decimal('35.00')),
    )
    for name, price in starter_items:
        MenuItem.objects.get_or_create(
            name__iexact=name,
            defaults={'name': name, 'price': price, 'is_available': True},
        )
    menu_items = MenuItem.objects.filter(is_available=True).filter(
        Q(name__iexact='Porrata') | Q(name__iexact='Dosa') | Q(name__iexact='Idli')
    ).order_by('id')
    return render(request, 'menu.html', {'table': table, 'menu_items': menu_items})

@login_required(login_url='login')
def submit_order_view(request, table_num):
    if request.method != 'POST':
        return redirect('home')

    table = get_object_or_404(Table, number=table_num)
    available_items = MenuItem.objects.filter(is_available=True).filter(
        Q(name__iexact='Porrata') | Q(name__iexact='Dosa') | Q(name__iexact='Idli')
    )
    selections = []
    for item in available_items:
        try:
            quantity = int(request.POST.get(f'qty_{item.id}', 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity < 0 or quantity > 50:
            messages.error(request, 'Please choose a quantity between 0 and 50.')
            return redirect('menu', table_number=table_num)
        if quantity:
            selections.append((item, quantity))

    if not selections:
        messages.error(request, 'Choose at least one food item before placing your order.')
        return redirect('menu', table_number=table_num)

    priority = request.POST.get('priority', 'medium')
    if priority not in {'low', 'medium', 'high'}:
        priority = 'medium'
    order = Order.objects.create(table=table, priority=priority)
    for item, quantity in selections:
        OrderItem.objects.create(order=order, menu_item=item, quantity=quantity)
    table.status = 'occupied'
    table.save()
    messages.success(request, f'Order #{order.id} was sent to the kitchen.')
    return redirect('home')


def kds_view(request):
    active_orders = Order.objects.exclude(status='completed').order_by('-priority', 'created_at')
    return render(request, 'kds.html', {'orders': active_orders})

def update_order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.GET.get('status')
    if new_status in ['preparing', 'completed']:
        order.status = new_status
        order.save()
        if new_status == 'completed':
            order.table.status = 'available'
            order.table.save()
    return redirect('kds')



def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        next_url = request.POST.get('next', '')
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect('home')
    return render(request, 'register.html', {'form': form, 'next': request.POST.get('next', request.GET.get('next', ''))})
