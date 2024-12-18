from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Agent, Package, Books

# Use the custom user model
User = get_user_model()

def homePage(request):
    return render(request, 'users/home.html')  

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')

        # Check if email or username already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        try:
            # Use create_user for proper password hashing
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
        except ValueError as e:
            messages.error(request, f"Registration failed: {str(e)}")
        except Exception as e:
            messages.error(request, 'An unexpected error occurred during registration.')

    return render(request, 'users/register.html')


def success_page(request):
    return render(request, "users/success.html")

@login_required
def home(request):
    return render(request, 'users/home.html')


def confirm_email(request):
    return render(request, 'users/confirm_email.html')


@login_required
def book_vacation_package(request):
    if request.method == 'POST':
        if not request.user.is_staff:
            return HttpResponseForbidden("You do not have permission to book a package.")

        user_id = request.POST.get('user_id')
        agent_id = request.POST.get('agent_id')
        package_id = request.POST.get('package_id')

        user = get_object_or_404(User, id=user_id)
        agent = get_object_or_404(Agent, id=agent_id)  # Assuming `id` field in Agent model
        package = get_object_or_404(Package, id=package_id)  # Assuming `id` field in Package model

        try:
            booking = Books.objects.create(user=user, agent=agent, package=package)
            return JsonResponse({
                'success': True,
                'message': 'Package booked successfully!',
                'booking_id': booking.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'bookings/book_package.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Flight, FlightBooking


@login_required
def book_flight(request):
    if request.method == "POST":
        flight_id = request.POST.get("flight_id")
        flight = Flight.objects.get(pk=flight_id)
        
        # Create a FlightBooking for the user
        FlightBooking.objects.create(
            user=request.user,
            flight=flight
        )
        return redirect("success_page")  # Redirect after successful booking
    
    flights = Flight.objects.all()
    return render(request, "users/book_flight.html", {"flights": flights})
