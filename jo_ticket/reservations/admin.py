from django.contrib import admin
from .models import Offer, Reservation, Cart, AdminStats

admin.site.register(Offer)
admin.site.register(Reservation)
admin.site.register(Cart)
admin.site.register(AdminStats)


