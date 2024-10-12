from django.contrib import admin
from django.urls import path, include
from reservations import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin_ventes/", views.admin_sales, name="admin_sales"),
    path('accounts/', include('django.contrib.auth.urls')),  # Inclut les URLs d'authentification par défaut de Django
    
    path("", views.home, name="home"),
    path("accueil/", views.home, name="home"),
    
    path("offres/", views.offers_list, name="offers_list"),
    path("panier/", views.cart, name="cart"),
    path('add_to_cart/<int:offer_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:offer_id>/', views.remove_from_cart, name='remove_from_cart'),  
    
    path('reserve_offer/<int:offer_id>/', views.reserve_offer, name='reserve_offer'),
    path('checkout/<int:reservation_id>/', views.checkout, name='checkout'),
    path("checkout/<int:reservation_id>/success/", views.payement_success, name="payement_success"),
    path("checkout/<int:reservation_id>/cancel/", views.payement_cancel, name="payement_cancel"),

    path("connexion/", auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('deconnexion/', views.custom_logout, name='logout'),
    path("inscription/", views.SignUpView.as_view(), name="signup"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
 
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    path('mon_compte/', views.account, name='account'),
    path('mon_compte/<int:reservation_id>', views.account_detail, name='account_detail'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
