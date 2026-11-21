from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Room, Room, StudentProfile

from django.db.models import Count, Q


from django.core.exceptions import ValidationError

class StudentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="Enter your first name or first and last name."
    )

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        username = ''.join(username.split())
        return username


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'admission_number',
            'phone_number',
            'course',
            'gender',
            'profile_photo',
        ]

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room']

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student

        available_rooms = []

        if student and student.gender:

            rooms = Room.objects.filter(
                is_available=True,
                hostel__gender=student.gender
            ).annotate(
                occupied_beds=Count(
                    'bookings',
                    filter=Q(bookings__status='Approved')
                )
            ).order_by('hostel_id', 'id')

            opened_hostels = set()

            for room in rooms:

                if room.hostel_id in opened_hostels:
                    continue

                if room.occupied_beds < room.room_capacity:
                    available_rooms.append(room)
                    opened_hostels.add(room.hostel_id)

        room_ids = [room.id for room in available_rooms]
        self.fields['room'].queryset = rooms.filter(
            id__in=room_ids
        ) if student and student.gender else Room.objects.none()

        self.fields['room'].label = "Select an Available Room"
        self.fields['room'].label_from_instance = (
            lambda room: (
                f"{room.hostel.hostel_name} | "
                f"Room {room.room_number} | "
                f"KSh {room.room_price} | "
                f"Occupied: {room.occupied_beds}/"
                f"{room.room_capacity} | "
                f"Remaining: "
                f"{room.room_capacity - room.occupied_beds} beds"
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.student:
            existing_booking = Booking.objects.filter(
            student=self.student,
            status__in=['Pending', 'Approved']
            ).exists()

        if existing_booking:
            raise ValidationError(
                "You already have an active room booking. "
                "Please wait for its outcome before booking again."
            )

        return cleaned_data