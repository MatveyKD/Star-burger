from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    latitude = models.DecimalField(
        'широта',
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class QuerySetManager(models.QuerySet):
    def get_total_cost(self):
        return self.annotate(total_cost=Sum(F("products__price") * F("products__quantity")))


class Order(models.Model):
    firstname = models.CharField(
        'Имя заказчика',
        max_length=20
    )
    lastname = models.CharField(
        'Фамилия заказчика',
        max_length=20
    )

    phonenumber = PhoneNumberField(
        "Номер телефона заказчика"
    )

    address = models.CharField(
        'Адрес заказа',
        max_length=40
    )

    comment = models.CharField(
        'Комментарий к заказу',
        max_length=40,
        blank=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        verbose_name='Какой ресторан готовит заказ',
        blank=True,
        null=True,
    )

    registered = models.DateTimeField(
        'Время регистрации заказа',
        default=timezone.now
    )
    called = models.DateTimeField(
        'Время звонка',
        null=True,
        blank=True
    )
    delivered = models.DateTimeField(
        'Время доставки',
        null=True,
        blank=True
    )

    statuses = [
        ('NP', 'Not processed'),
        ('CK', 'Cooking'),
        ('DL', 'Delivering'),
        ('CP', 'Completed')
    ]

    payments = [
        ('EL', 'Electronic'),
        ('CS', 'Cash')
    ]

    status = models.CharField(
        'Статус заказа',
        choices=statuses,
        max_length=13,
        default='NP'
    )

    payment = models.CharField(
        'Способ оплаты',
        max_length=10,
        choices=payments,
        default='CS'
    )

    latitude = models.DecimalField(
        'широта',
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True
    )

    objects = QuerySetManager.as_manager()

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"


class OrderProduct(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="Заказанный продукт",
        on_delete=models.CASCADE,
    )

    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="products"
    )

    quantity = models.IntegerField(
        verbose_name="Количество продуктов",
        default=1,
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        'Цена продкута',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
