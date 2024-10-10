from django.db import models
from django.contrib.auth.models import User
import uuid


class Offer(models.Model):
    OFFER_TYPE = [
        ("solo", "Solo"),
        ("duo", "Duo"),
        ("famille", "Famille"),
    ]
    
    name = models.CharField(max_length=100, choices=OFFER_TYPE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='offers/', default='offers/default.jpg')
    decription = models.TextField(default='')
    people = models.IntegerField()
    
    def __str__(self):
        return f'Offre: {self.get_name_display()} - {self.price}€'
    

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ManyToManyField(Offer)
    created_at = models.DateTimeField(auto_now_add=True)
    payement_key = models.CharField(max_length=255, editable=False)
    security_key = models.UUIDField(default=uuid.uuid4, editable=False)
    is_paid = models.BooleanField(default=False)
    qr_code = models.TextField(default='')
    
    def __str__(self):
        offers = ', '.join([offer.get_name_display() for offer in self.offer.all()])
        return f'Reservation # {self.id} de {self.user.username} pour {offers}'
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offers = models.ManyToManyField(Offer)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Panier de {self.user.username} - {self.offers}'
    

class AdminStats(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    total_reservations = models.IntegerField(default=0)