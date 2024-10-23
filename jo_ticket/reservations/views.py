from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import Offer, Reservation, Cart, AdminStats
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from .forms import ContactUsForm
import uuid
import stripe
import io
import qrcode
import base64


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def offers_list(request):
    offers = Offer.objects.all()
    cart, created= Cart.objects.get_or_create(user=request.user)
    total = sum([offer.price for offer in cart.offers.all()])
    return render(request, 'offers_list.html', {'offers': offers, 'total': total})

@login_required
def reserve_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    reservation = Reservation.objects.create(user=request.user)
    reservation.offer.set(cart.offers.all())
    return redirect('checkout', reservation.id)

@login_required
def checkout(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    cart = Cart.objects.get(user=request.user)
    total = sum([offer.price for offer in cart.offers.all()])
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY
    
    # Si le panier est vide, renvoyer un message d'erreur
    if not cart.offers.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect('cart')

    # Créer les lignes d'élément Stripe pour chaque offre dans le panier
    line_items = []
    for offer in cart.offers.all():
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': offer.name,
                },
                'unit_amount': int(offer.price * 100),  # Prix converti en centimes
            },
            'quantity': 1,
        })

    # Créer une session de paiement Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        customer_email=request.user.email,
        success_url=request.build_absolute_uri('/checkout/{}/success/'.format(reservation.id)),
        cancel_url=request.build_absolute_uri('/checkout/{}/cancel/'.format(reservation.id)),
    )

    # # Enregistrer la clé de paiement dans la réservation avant de lancer le paiement
    reservation.payement_key = session.id
    reservation.save()

    # Rendre la page du checkout avec les informations Stripe
    return render(request, 'checkout.html', {
        'session_id': session.id,
        'stripe_public_key': stripe_public_key,
        'total': total,
        'reservation': reservation,
        'offer': cart.offers.all()
    })


def send_confirmation_email(user):
    send_mail(
        f'Réservation #{Reservation.id} confirmée',
        'Votre réservation a bien été enregistrée',
        f'Total de l\'achat: {Reservation.offer.price}€',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            self.send_confirmation_email(user)
        return response
    
    def send_confirmation_email(self, user):
        subject = 'Confirmation de votre inscription'
        message = render_to_string('welcome_email.html', {'user': user})  # Chemin correct vers le template
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

def account(request):
    reservations = Reservation.objects.filter(user=request.user)
    paid_reservations = Reservation.objects.filter(user=request.user, is_paid=True)
    return render(request, 'account.html', {'user':request.user, 'reservations': reservations, 'paid_reservations': paid_reservations})

def account_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    total_price = sum([offer.price for offer in reservation.offer.all()])
    return render(request, 'account_detail.html', {'reservation': reservation, 'total_price': total_price})

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')

@login_required
def add_to_cart(request, offer_id):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=offer_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Vérifiez si l'offre est déjà dans le panier
        if cart.offers.filter(id=offer_id).exists():
            messages.info(request, 'Le billet est déjà dans votre panier.')
            return JsonResponse({'message': 'Le billet est déjà dans votre panier.'}, status=200)
        
        cart.offers.add(offer)
        messages.success(request, 'Le billet a été ajouté au panier !')
        return JsonResponse({'message': 'Offre ajoutée au panier !'}, status=200)
    
    return JsonResponse({'error': 'Requête invalide.'}, status=400)


@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        offers = cart.offers.all()
        total = sum([offer.price for offer in cart.offers.all()])
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
        offers = []
        total = 0
    return render(request, 'cart.html', {'cart': cart, 'total': total, 'offers': offers})


def remove_from_cart(request, offer_id):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        offer = get_object_or_404(Offer, id=offer_id)
        cart.offers.remove(offer)
        messages.success(request, 'Offre supprimée !')
        return JsonResponse({'message': 'Le ticket a été retiré de votre panier.'}, status=200)
    return JsonResponse({'error': 'Requête invalide.'}, status=400)

@login_required
def payement_success(request, reservation_id):
    cart = Cart.objects.get(user=request.user)
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    session = stripe.checkout.Session.retrieve(reservation.payement_key)
    
    if session.payment_status == 'paid':    
        stripe_email = session.customer_details.email
        
        items_detail = ""
        total_price = 0
        
        for offer in cart.offers.all():
            items_detail += f"{offer.name} - \n"
            total_price += offer.price

        qr_data = f"""
        Réservation: {reservation.id}
        Offre: {items_detail}
        Prix: {total_price}€
        Date: {reservation.created_at}
        Acheté par: {request.user.username}
        Clef de sécurité: {reservation.security_key}
        Clef d'achat: {reservation.payement_key}
        """
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer)
        buffer.seek(0)  # Assurez-vous que le buffer est réinitialisé avant l'attachement
        
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        reservation.qr_code = qr_image
        reservation.save()
        
        subject = 'Confirmation de votre achat'
        html_content = render_to_string('email_template.html', {
            'reservation': reservation,
            'items_detail': items_detail,
            'total_price': total_price,
            'account_url': request.build_absolute_uri('/account/')
        })
        
        recipient_list = [stripe_email]  
        email = EmailMultiAlternatives(subject, html_content, 'ecmosdev@gmail.com', recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.content_subtype = 'html'  # Définir le contenu en HTML
        email.attach('qrcode.png', buffer.getvalue(), 'image/png')
        email.send()
        
        # Récupérer toutes les réservations payées de l'utilisateur
        paid_reservations = Reservation.objects.filter(user=request.user, is_paid=True)

        for offer in cart.offers.all():
            reservation.offer.set(cart.offers.all())
            reservation.is_paid = True 
            reservation.save()

        cart.offers.clear()
        return render(request, 'payement_success.html', {'reservation': reservation, 'qr_image': qr_image, 'paid_reservations': paid_reservations, 'total_price': total_price})
    else:
        messages.error(request, 'Le paiement a échoué.')
        return redirect('cart')

    
def contact(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        
        if form.is_valid():
            send_mail(subject=f"Message from {form.cleaned_data['nom'] or 'Anonyme'} - {form.cleaned_data['email']} via MerchEx Contact Form Us Page",
            message=form.cleaned_data['message'],
            from_email=form.cleaned_data['email'],
            recipient_list=['ecmosdev@gmail.com'],)
            messages.success(request, 'Votre message a bien été envoyé.')
        return redirect('email-sent')
    else:
        form = ContactUsForm()
    return render (request, "contact.html", {"form": form})

def email_sent(request):
    return render(request, "email_sent.html")

def payement_cancel(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    return render(request, 'payement_cancel.html', {'reservation':reservation})

def admin_sales(request):
    sales_data = AdminStats.objects.all()
    return render(request, 'admin_sales.html', {'sales_data': sales_data})

def base(request):
    return render(request, "base.html")

def base_2(request):
    return render(request, "base_2.html")

def home(request):
    return render(request, "home.html")

def error_404(request, exception):
    return render(request, '404.html', status=404)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'votre_webhook_secret_de_stripe'

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        reservation = Reservation.objects.get(payement_key=session['id'])
        reservation.is_paid = True
        reservation.save()

    return JsonResponse({'status': 'success'}, status=200)
