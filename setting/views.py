from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def settings_page(request):
    return render(request, 'setting.html')

@login_required
def update_contact_info(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        request.user.email = email
        request.user.profile.phone_number = phone_number
        request.user.save()
        request.user.profile.save()

        return redirect('setting:settings_page')

    return render(request, 'setting.html')

@login_required
def change_password(request):
    # Add your change_password logic here
    return render(request, 'change_password.html')

@login_required
def privacy_settings(request):
    # Add your privacy_settings logic here
    return render(request, 'privacy_settings.html')

@login_required
def notification_settings(request):
    # Add your notification_settings logic here
    return render(request, 'notification_settings.html')

@login_required
def blocked_users(request):
    # Add your blocked_users logic here
    return render(request, 'blocked_users.html')

@login_required
def linked_accounts(request):
    # Add your linked_accounts logic here
    return render(request, 'linked_accounts.html')

@login_required
def delete_account(request):
    # Add your delete_account logic here
    return render(request, 'delete_account.html')
