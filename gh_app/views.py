from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from gh_app.models import Donation, Institution


class LandingPage(View):
    def get(self, request):

        donations = Donation.objects.all()
        donations_quantity = 0

        for donation in donations:
            donations_quantity += donation.quantity

        institutions = Institution.objects.filter(donation__isnull=False)
        institutions_quantity = institutions.count()

        foundations = institutions.filter(type=1)
        organisations = institutions.filter(type=2)
        collections = institutions.filter(type=3)

        return render(request, 'index.html', {"d_quantity": donations_quantity,
                                              "i_quantity": institutions_quantity,
                                              "foundations": foundations,
                                              "organisations": organisations,
                                              "collections": collections})


class AddDonation(View):
    def get(self, request):
        return render(request, 'form.html')


class Login(View):
    def get(self, request):
        return render(request, 'login.html')


class Register(View):
    def get(self, request):
        return render(request, 'register.html')
