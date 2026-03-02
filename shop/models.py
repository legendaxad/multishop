from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**kwargs):
        if not email:
            raise ValueError("Email must be fill")
        email=self.normalize_email(email=email)
        user=self.model(email=email,**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**kwargs):
        kwargs.setdefault("is_staff",True)
        kwargs.setdefault("is_superuser",True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Staff status must be True")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Staff status must be True")

        return self.create_user(email=email,password=password,**kwargs)

class User(AbstractUser):
    choice_countries = [
        ("Uzbekistan","Uzbekistan"),
        ("Kazakhstan","Kazakhstan"),
        ("Korea","Korea"),
        ("Kyrgyzstan","Kyrgyzstan"),
    ]
    username = None
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=13)
    country=models.CharField(max_length=15,choices=choice_countries,default="Korea")
    city=models.CharField(max_length=30)
    region=models.CharField(max_length=30)
    address=models.CharField(max_length=60)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Category(models.Model):
    title=models.CharField(max_length=50)
    image=models.ImageField(upload_to='images/categories')


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Product(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.title

    def get_image(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return "https://png.pngtree.com/png-vector/20221125/ourmid/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"
        return "https://png.pngtree.com/png-vector/20221125/ourmid/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"

class ProductType(models.Model):
    SIZE_CHOICES = [
        ("xs","extra small"),
        ("s","small"),
        ("m","medium"),
        ("l","large"),
        ("xl","extra large")
    ]
    COLOR_CHOICES = [
        ("black","black"),
        ("white","white"),
        ("red","red"),
        ("green","green"),
        ("blue","blue")
    ]
    size = models.CharField(max_length=15, choices=SIZE_CHOICES, default="m")
    color = models.CharField(max_length=15, choices=COLOR_CHOICES, default="white")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="types")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("product",'size','color')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images/products/")

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"


class Slider(models.Model):
    title = models.CharField(max_length=250)
    name=models.CharField(max_length=200)
    image = models.ImageField(upload_to="images/Slider/")

    def __str__(self):
        return self.title


class Banner(models.Model):
    title=models.CharField(max_length=100)
    season=models.CharField(max_length=100)
    image=models.ImageField(upload_to="images/banner")

class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.full_name

class Likes(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.email}-{self.product.title}"


class Basket(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    quantity=models.PositiveIntegerField(default=1)

    def get_total_sale(self):
        if self.product.types.first().sale:
            return self.product.types.first().sale * self.quantity
        return self.product.types.first().price * self.quantity

    def get_total_price(self):
        if self.product.types.first().price:
            return self.product.types.first().price * self.quantity
        return self.product.types.first().price * self.quantity

    class Meta:
        unique_together = ('user', 'product')


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.title}"









