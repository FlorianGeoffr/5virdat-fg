from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.        

class RefundedChoices(models.TextChoices):
	YES = 'YES', 'Yes'
	NO = 'NO', 'No'

class CurrencyChoices(models.TextChoices):
	USD = 'USD', 'USD'
	EUR = 'EUR', 'EUR'

class ModelChoices(models.TextChoices):
	ITEMS    = 'ITEMS', _('Items')
	SALES    = 'SALES', _('Sales')
	PRODUCTS = 'PRODUCTS', _('Products')
		
class PageItems(models.Model):
	parent = models.CharField(max_length=255, choices=ModelChoices.choices)
	items_per_page = models.IntegerField(default=25)
	
class HideShowFilter(models.Model):
	parent = models.CharField(max_length=255, choices=ModelChoices.choices)
	key = models.CharField(max_length=255)
	value = models.BooleanField(default=False)

	def __str__(self):
		return self.key

class ModelFilter(models.Model):
	parent = models.CharField(max_length=255, choices=ModelChoices.choices)
	key = models.CharField(max_length=255)
	value = models.CharField(max_length=255)

	def __str__(self):
		return self.key	
			
class Sales(models.Model):
	ID = models.AutoField(primary_key=True)
	Product = models.TextField(blank=True, null=True)
	BuyerEmail = models.EmailField(blank=True, null=True)
	PurchaseDate = models.DateField(blank=True, null=True)
	Country = models.TextField(blank=True, null=True)
	Price = models.FloatField(blank=True, null=True)
	Refunded = models.CharField(max_length=20, choices=RefundedChoices.choices, default=RefundedChoices.NO)
	Currency = models.CharField(max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
	Quantity = models.IntegerField(blank=True, null=True)

class Products(models.Model):
	ID = models.AutoField(primary_key=True)
	Name = models.TextField(blank=True, null=True)	
	Description = models.TextField(blank=True, null=True)

# Don't remove this mark
### ### Below code is Generated ### ###
