from django.shortcuts import render

# Create your views here.

def showAdminPage(request):
    return render(request, 'adminpage.html')
