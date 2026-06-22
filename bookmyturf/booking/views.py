from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Booking

# Try to import WhatsApp helper — works only after twilio is installed
try:
    from .whatsapp import send_booking_confirmation
    WHATSAPP_ENABLED = True
except ImportError:
    WHATSAPP_ENABLED = False


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect('/login/')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')

        return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def turfs(request):
    return render(request, 'turfs.html')


@login_required
def booking(request):
    if request.method == 'POST':
        booking_data = {
            'name':      request.POST.get('name'),
            'phone':     request.POST.get('phone'),
            'email':     request.POST.get('email'),
            'turf_type': request.POST.get('turf_type'),
            'date':      request.POST.get('date'),
            'time_slot': request.POST.get('time_slot'),
        }

        # Save to database
        Booking.objects.create(
            name         = booking_data['name'],
            phone        = booking_data['phone'],
            email        = booking_data['email'],
            turf_type    = booking_data['turf_type'],
            booking_date = booking_data['date'],
            time_slot    = booking_data['time_slot'],
        )

        # Send WhatsApp confirmation if twilio is installed
        whatsapp_sent = False
        if WHATSAPP_ENABLED:
            whatsapp_sent = send_booking_confirmation(booking_data)

        return render(request, 'success.html', {
            **booking_data,
            'whatsapp_sent': whatsapp_sent,
        })

    return render(request, 'booking.html')