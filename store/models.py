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


category_choices = (
    ('color', 'color'),
    ('size', 'size'),
    ('condition', 'condition'),
)

# テンプレートでの振り分けを簡単にするためにmanagerクラスでカラーとサイズに分けた値を取得する


# class VariationManager(models.Manager):

# def colors(self):
# return super(VariationManager,# self).filter(variation_choices='color', is_active=True)

# def sizes(self):
# return super(VariationManager, self).filter(variation_choices="size", is_active=True)

# model内でのqueryの発酵によりn+1問題が発生してないか確認する必要性がある


class Variation(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product")
    variation_choices = models.CharField(
        max_length=100, choices=category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    #objects = VariationManager()

    def __unicode__(self):
        return self.product
