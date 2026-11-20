from django.contrib import admin
from .models import StudentProfile
from .models import StudentProfile, Hostel
from .models import StudentProfile, Hostel, Room
from .models import StudentProfile, Hostel, Room, Booking
from .models import Payment


class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        'admission_number',
        'phone_number',
        'course',
        'created_at',
    )


admin.site.register(StudentProfile, StudentProfileAdmin)

class HostelAdmin(admin.ModelAdmin):
    list_display = (
        'hostel_name',
        'gender',
        'location',
        'created_at',
    )

    list_filter = ('gender',)

    search_fields = (
        'hostel_name',
        'location',
    )

admin.site.register(Hostel, HostelAdmin)

class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'hostel',
        'room_number',
        'room_capacity',
        'room_price',
        'is_available',
    )

    list_filter = ('hostel', 'is_available')

    search_fields = ('room_number', 'hostel__hostel_name')


admin.site.register(Room, RoomAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'room',
        'booking_date',
        'status',
    )

    list_filter = ('status', 'booking_date')

    search_fields = (
        'student__admission_number',
        'room__room_number',
    )

admin.site.register(Booking, BookingAdmin)

admin.site.register(Payment)