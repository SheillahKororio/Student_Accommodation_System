from django.db import models
from django.conf import settings



class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    admission_number = models.CharField(
        max_length=30,
        unique=True
    )

    phone_number = models.CharField(max_length=20)
    course = models.CharField(max_length=100) 
    GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]


    gender = models.CharField(
    max_length=10,
    choices=GENDER_CHOICES,
    null=True,
    blank=True
) 
    profile_photo = models.ImageField(
    upload_to='student_photos/',
    null=True,
    blank=True
)

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.admission_number

class Hostel(models.Model):

    hostel_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    GENDER_CHOICES = [
        ('Male', "Male Hostel"),
        ('Female', "Female Hostel"),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostel_name

class Room(models.Model):

    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name='rooms'
    )

    room_number = models.CharField(max_length=20)
    room_image = models.ImageField(
    upload_to='room_photos/',
    blank=True,
    null=True
)
    room_capacity = models.PositiveIntegerField()
    room_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hostel.hostel_name} - Room {self.room_number}"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    booking_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='Pending'
    )

    def __str__(self):
        return f"{self.student.admission_number} - {self.room.room_number}"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    phone_number = models.CharField(max_length=20)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mpesa_receipt_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    result_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.booking.student.admission_number} - {self.status}"
