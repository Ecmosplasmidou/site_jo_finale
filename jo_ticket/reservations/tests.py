from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Offer, Reservation, Cart
from django.urls import reverse

class OfferModelTest(TestCase):
    def setUp(self):
        self.offer = Offer.objects.create(
            name="solo", price=100.00, people=1, decription="Offre Solo"
        )
    
    def test_offer_creation(self):
        self.assertEqual(self.offer.name, "solo")
        self.assertEqual(self.offer.price, 100.00)
        self.assertEqual(self.offer.people, 1)
        self.assertEqual(str(self.offer), "Offre: Solo - 100.00€")


class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.offer = Offer.objects.create(
            name="solo", price=100.00, people=1, decription="Offre Solo"
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.reservation.offer.add(self.offer)
    
    def test_reservation_creation(self):
        self.assertEqual(self.reservation.user.username, "testuser")
        self.assertTrue(self.reservation.offer.filter(name="solo").exists())
        self.assertFalse(self.reservation.is_paid)

    def test_str_representation(self):
        self.assertEqual(str(self.reservation), f"Reservation # {self.reservation.id} de testuser pour Solo")


class OffersListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.offer = Offer.objects.create(name="solo", price=100.00, people=1)
        self.client = Client()

    def test_offers_list_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('offers_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers_list.html')
        self.assertIn('offers', response.context)
        self.assertContains(response, '100.00')

class CartViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.offer = Offer.objects.create(name="solo", price=100.00, people=1)
        self.client = Client()
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart.offers.add(self.offer)

    def test_cart_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')
        self.assertIn('offers', response.context)
        self.assertIn(self.offer, response.context['offers'])
        self.assertContains(response, '100.00')

class CheckoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.offer = Offer.objects.create(name="solo", price=100.00, people=1)
        self.client = Client()
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart.offers.add(self.offer)
        self.reservation = Reservation.objects.create(user=self.user)
        self.reservation.offer.set(self.cart.offers.all())
    
    def test_checkout_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('checkout', args=[self.reservation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')
        self.assertIn('total', response.context)
        self.assertIn('session_id', response.context)

class PaymentSuccessViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.offer = Offer.objects.create(name="solo", price=100.00, people=1)
        self.client = Client()
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart.offers.add(self.offer)
        self.reservation = Reservation.objects.create(user=self.user)
        self.reservation.offer.set(self.cart.offers.all())
        self.reservation.payement_key = "test_payment_key"
        self.reservation.save()

    def test_payment_success_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('payement_success', args=[self.reservation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payement_success.html')
        self.assertIn('qr_image', response.context)
        self.assertIn('total_price', response.context)
        
        
class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_view(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'testuser@example.com'
        })
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertRedirects(response, reverse('home')) 

        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)


