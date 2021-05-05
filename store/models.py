from django.db import models
from category.models import Category
from django.urls import reverse
# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    descritpion = models.TextField(max_length=500)
    price = models.IntegerField()
    stock = models.IntegerField()
    img = models.FileField(upload_to='product')
    is_available = models.BooleanField(default=True)
    on_created = models.DateTimeField(auto_now_add=True)
    on_modified = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,)

    def get_url(self):
        return reverse('store:products_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
