from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Organization(AbstractUser):

    # organization related
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=1000, blank=True)
    itn = models.CharField(max_length=16)
    address = models.CharField(max_length=100)

    username = None

    # creator related
    email = models.EmailField(unique=True)
    patronymic = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=30)
    website = models.CharField(max_length=30, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [email]

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.CharField(max_length=60)
    review = models.TextField(max_length=1000)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='reviews_left')
    rating = models.SmallIntegerField(default=1,
                                      validators=[MinValueValidator(1), MaxValueValidator(5)])
    date_created = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):

    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


STATUS_NOT_ACCEPTED = 0
STATUS_ACCEPTED = 1
STATUS_COMPLETED = 2

CATEGORY_IT = 0
CATEGORY_FINANCE = 1
CATEGORY_STAFF = 2
CATEGORY_MARKETING = 3
CATEGORY_RETAIL = 4
CATEGORY_OTHER = 5


class Order(models.Model):

    STATUS_CHOICES = (
        (STATUS_NOT_ACCEPTED, 'not accepted'),
        (STATUS_ACCEPTED, 'accepted'),
        (STATUS_COMPLETED, 'completed'),
    )

    CATEGORY_CHOICES = (
        (CATEGORY_IT, 'IT'),
        (CATEGORY_FINANCE, 'finance'),
        (CATEGORY_STAFF, 'staff'),
        (CATEGORY_MARKETING, 'marketing'),
        (CATEGORY_RETAIL, 'retail'),
        (CATEGORY_OTHER, 'other')
    )

    name = models.CharField(max_length=120)
    description = models.TextField(max_length=1000, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='orders')
    performer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL, related_name='accepted_orders')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_NOT_ACCEPTED, db_index=True)
    category = models.SmallIntegerField(choices=CATEGORY_CHOICES, default=CATEGORY_OTHER, db_index=True)
    tags = models.ManyToManyField(Tag, related_name='orders')

    def __str__(self):
        return self.name


class OrderRequest(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    performer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(max_length=1000, blank=True)
