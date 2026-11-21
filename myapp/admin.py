from django.contrib import admin
from .models import StudentProfile, Hostel, Room, Booking, Payment


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'admission_number',
        'phone_number',
        'course',
        'gender',
        'profile_photo',
        'created_at',
    )

    search_fields = (
        'admission_number',
        'phone_number',
        'course',
        'user__username',
    )

    readonly_fields = ('photo_preview',)

    fields = (
        'user',
        'admission_number',
        'phone_number',
        'course',
        'gender',
        'profile_photo',
        'photo_preview',
        'created_at',
    )

    def get_student_name(self, obj):
        return obj.user.username

        get_student_name.short_description = 'Student Name'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'

    def photo_preview(self, obj):
        if obj.profile_photo:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" width="120" height="120" style="object-fit:cover;" />',
                obj.profile_photo.url
            )
        return "No photo uploaded"

    photo_preview.short_description = 'Student Photo'

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