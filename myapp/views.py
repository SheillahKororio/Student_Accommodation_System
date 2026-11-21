import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Count
from .forms import (
    StudentRegistrationForm,
    StudentProfileForm,
    BookingForm
)

from django.shortcuts import render, get_object_or_404
from .models import Hostel, Room, Booking, Payment
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')



def register(request):

    if request.method == 'POST':
        user_form = StudentRegistrationForm(request.POST)
        profile_form = StudentProfileForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():

            with transaction.atomic():

                user = user_form.save()

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

            return redirect('myapp:login')

    else:
        user_form = StudentRegistrationForm()
        profile_form = StudentProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'register.html', context)


def student_login(request):
    if request.method == 'POST':

        login_data = request.POST.copy()

        # Remove spaces from the username
        username = login_data.get('username', '')
        login_data['username'] = ''.join(username.split())

        form = AuthenticationForm(
            request,
            data=login_data
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('myapp:dashboard')

    else:
        form = AuthenticationForm()

    return render(
        request,
        'login.html',
        {'form': form}
    )

@login_required
def student_dashboard(request):

    profile = request.user.studentprofile

    context = {
        'profile': profile,
    }

    return render(request, 'dashboard.html', context)

def student_logout(request):
    logout(request)
    return redirect('myapp:login')

@login_required
def book_room(request):
    student = request.user.studentprofile

    if request.method == 'POST':
        form = BookingForm(request.POST, student=student)

        if form.is_valid():
            room_id = form.cleaned_data['room'].id

            with transaction.atomic():
                room = Room.objects.select_for_update().get(id=room_id)

                occupied_beds = Booking.objects.filter(
                    room=room,
                    status='Approved'
                ).count()

                if occupied_beds >= room.room_capacity:
                    form.add_error(
                        'room',
                        'Sorry, this room is already full.'
                    )

                elif Booking.objects.filter(
                    student=student,
                    status__in=['Pending', 'Approved']
                ).exists():
                    form.add_error(
                        None,
                        'You already have an active booking.'
                    )

                else:
                    booking = form.save(commit=False)
                    booking.student = student
                    booking.save()

                    return redirect('myapp:make_payment', booking_id=booking.id)

    else:
        form = BookingForm(student=student)

    return render(request, 'booking.html', {'form': form})

def accommodation(request):
    return render(request, 'accommodation.html')


def hostel_rooms(request, hostel_type):
    hostel_gender = {
        'kings': 'Male',
        'queens': 'Female',
    }

    gender = hostel_gender.get(hostel_type.lower())

    if not gender:
        from django.http import Http404
        raise Http404("Hostel not found")

    hostel = get_object_or_404(Hostel, gender=gender)
    rooms = Room.objects.filter(hostel=hostel)

    return render(request, 'hostel_rooms.html', {
        'hostel': hostel,
        'rooms': rooms,
    })

@login_required
def make_payment(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        student=request.user.studentprofile
    )

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            messages.error(request, 'Please enter your M-Pesa phone number.')
            return redirect('myapp:make_payment', booking_id=booking.id)

        amount = booking.room.room_price

        payment = Payment.objects.create(
            booking=booking,
            phone_number=phone_number,
            amount=amount,
            status='Pending'
        )

        try:
            from .mpesa import initiate_stk_push

            response = initiate_stk_push(
                phone_number,
                amount,
                booking.id
            )

            payment.checkout_request_id = response.get('CheckoutRequestID')
            payment.merchant_request_id = response.get('MerchantRequestID')
            payment.result_description = response.get('CustomerMessage', '')
            payment.save()

            messages.success(
                request,
                'Payment request sent. Check your phone and enter your M-Pesa PIN.'
            )

        except Exception as e:
            payment.status = 'Failed'
            payment.result_description = str(e)
            payment.save()

            messages.error(request, 'Could not initiate payment. Please try again.')

        return redirect('myapp:dashboard')

    return render(request, 'payment.html', {'booking': booking})

@csrf_exempt
def mpesa_callback(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request'}, status=405)

    try:
        data = json.loads(request.body)

        callback = data['Body']['stkCallback']

        checkout_id = callback['CheckoutRequestID']
        result_code = callback['ResultCode']
        result_description = callback.get('ResultDesc', '')

        payment = Payment.objects.get(
            checkout_request_id=checkout_id
        )

        payment.result_description = result_description

        if result_code == 0:
            payment.status = 'Successful'

            items = callback.get('CallbackMetadata', {}).get('Item', [])

            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')

        else:
            payment.status = 'Failed'

        payment.save()

        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

    except Payment.DoesNotExist:
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Payment not found'})

    except Exception:
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Callback received'})