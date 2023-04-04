from django.contrib import messages
from django.contrib.auth import authenticate, login, password_validation, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from gh_app.models import Donation, Institution, Category


# from gh_app.tokens import account_activation_token


class LandingPage(View):
    def get(self, request):

        donations = Donation.objects.all()
        donations_quantity = 0

        for donation in donations:
            donations_quantity += donation.quantity

        # institutions = Institution.objects.filter(donation__isnull=False).distinct("id")
        institutions = Institution.objects.exclude(donation=None)
        institutions_quantity = institutions.count()

        foundations = institutions.filter(type=1)
        organizations = institutions.filter(type=2)
        collections = institutions.filter(type=3)

        return render(request, 'index.html', {"d_quantity": donations_quantity,
                                              "i_quantity": institutions_quantity,
                                              "foundations": foundations,
                                              "organizations": organizations,
                                              "collections": collections})


class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        username = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        error_msg = ''

        if password != password2:
            error_msg = "Podane hasła nie są identyczne!\n"

        if User.objects.filter(username=username).exists():
            error_msg += "Podany użytkownik już istnieje!\n"

        try:
            validate_email(username)
        except ValidationError:
            error_msg += "Niepoprawny adres email!"

        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            error_msg += str(e.messages)

        if error_msg:
            return render(request, "register.html", {'error_msg': error_msg})

        user = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        password=password,
                                        is_active=False)

        return redirect(reverse("login"))


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(reverse('landing_page'))
        else:
            # messages.error(request, "Błędne dane!")  # WYSWIETLA SIE W INNYM MIEJSCU
            # return redirect(reverse('register'))
            error_msg = "Podano błędne dane!"
            return render(request, "login.html", {'error_msg': error_msg})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('landing_page'))


class UserView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        donations = Donation.objects.filter(user=user).order_by("pick_up_date", "pick_up_date")
        return render(request, 'user.html', {"donations": donations})

    def post(self, request):

        categories = request.POST.getlist('categories')
        quantity = request.POST.get('bags')
        institution_name = request.POST.get('institution')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('postcode')
        phone_number = request.POST.get('phone')
        pick_up_date = request.POST.get('data')
        pick_up_time = request.POST.get('time')
        pick_up_comment = request.POST.get('more_info')
        user = request.user

        try:
            institution = Institution.objects.get(name=institution_name)
        except ObjectDoesNotExist:
            return redirect(reverse('add_donation'))

        donation = Donation.objects.create(quantity=quantity, institution=institution, address=address,
                                           phone_number=phone_number, city=city, zip_code=zip_code,
                                           pick_up_date=pick_up_date, pick_up_time=pick_up_time,
                                           pick_up_comment=pick_up_comment, user=user)

        for category in categories:
            try:
                donation.categories.add(Category.objects.get(name=category))
            except ObjectDoesNotExist:
                continue

        return redirect(reverse('donate_confirmation'))


class AddDonation(LoginRequiredMixin, View):
    def get(self, request):

        categories = Category.objects.all()
        institutions = Institution.objects.all()
        return render(request, 'form.html', {"categories": categories,
                                             "institutions": institutions})


class DonateConfirmation(View):
    def get(self, request):
        return render(request, "form-confirmation.html")


class EditUser(View):
    def get(self, request, id):

        user = User.objects.get(id=id)
        logged_user = request.user

        if logged_user != user:
            return redirect(reverse('landing_page'))

        return render(request, 'edit_user.html')

    def post(self, request, id):

        user = User.objects.get(id=id)
        logged_user = request.user
        if logged_user != user:
            return redirect(reverse('landing_page'))

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password1']

        if user.check_password(password) is False:
            error_msg = "Błędne hasło!"
            return render(request, "edit_user.html", {'error_msg': error_msg})

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        return redirect(reverse('user'))


class EditPassword(View):
    def get(self, request, id):
        user = User.objects.get(id=id)
        logged_user = request.user
        if logged_user != user:
            return redirect(reverse('landing_page'))
        return render(request, 'edit_password.html')

    def post(self, request, id):
        user = User.objects.get(id=id)
        logged_user = request.user
        if logged_user != user:
            return redirect(reverse('landing_page'))

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        old_password = request.POST.get('old_password')

        if password1 != password2:
            error_msg = "Podane hasła nie są takie same!"
            return render(request, "edit_password.html", {'error_msg': error_msg})

        if user.check_password(old_password) is False:
            error_msg = "Błędne hasło!"
            return render(request, "edit_password.html", {'error_msg': error_msg})

        user.set_password(password1)
        user.save()

        return redirect(reverse('login'))
