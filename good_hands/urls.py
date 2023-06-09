"""good_hands URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gh_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LandingPage.as_view(), name='landing_page'),

    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('user/', views.UserView.as_view(), name='user'),
    path('edit/<int:id>/', views.EditUser.as_view(), name='edit'),
    path('edit_password/<int:id>/', views.EditPassword.as_view(), name='edit_password'),

    path('add-donation/', views.AddDonation.as_view(), name='add_donation'),
    path('donate-confirmation/', views.DonateConfirmation.as_view(), name='donate_confirmation'),

]
