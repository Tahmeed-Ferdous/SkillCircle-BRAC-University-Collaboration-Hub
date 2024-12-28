from django.shortcuts import render, redirect, get_object_or_404
from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from post.models import Post, Follow, Stream

from authy.models import Profile
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.urls import resolve, reverse
from django.db import transaction


# Create your views here.
def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	# 1
	# profile = Profile.objects.raw("SELECT * FROM profile WHERE user_id = %s LIMIT 1", [user.id])

	url_name = resolve(request.path).url_name
	
	if url_name == 'profile':
		posts = Post.objects.filter(user=user).order_by('-posted')\
		# 2
		# posts = Post.objects.raw("SELECT * FROM post WHERE user_id = %s ORDER BY posted DESC", [user.id])


	else:
		posts = profile.favorites.all()

	#Profile info box
	posts_count = Post.objects.filter(user=user).count()
	# 3
	# posts_count = Post.objects.raw("SELECT COUNT(*) FROM post WHERE user_id = %s", [user.id])

	following_count = Follow.objects.filter(follower=user).count()
	# 4
	# following_count=Follow.objects.raw("SELECT COUNT(*) FROM follow WHERE user_id =%s",[user.id])
	followers_count = Follow.objects.filter(following=user).count()
	#5
	# followers_count=Follow.objects.raw("SELECT COUNT(*) FROM follow WHERE user_id=%s",[user.id])

	#follow status
	follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
	# 6
	# follow_status = Follow.objects.raw("SELECT 1 FROM follow WHERE following_id = %s AND follower_id = %s LIMIT 1", [user.id, request.user.id]).exists()

	#Pagination
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page')
	posts_paginator = paginator.get_page(page_number)

	template = loader.get_template('profile.html')

	context = {
		'posts': posts_paginator,
		'profile':profile,
		'following_count':following_count,
		'followers_count':followers_count,
		'posts_count':posts_count,
		'follow_status':follow_status,
		'url_name':url_name,
	}

	return HttpResponse(template.render(context, request))

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('login')


def Signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, password=password)
			return redirect('login')
	else:
		form = SignupForm()
	
	context = {
		'form':form,
	}

	return render(request, 'signup.html', context)


@login_required
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change_password_done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'change_password.html', context)

def PasswordChangeDone(request):
	return render(request, 'change_password_done.html')


@login_required
def EditProfile(request):
	user = request.user.id
	profile = Profile.objects.get(user__id=user)

	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES)
		if form.is_valid():
			profile.picture = form.cleaned_data.get('picture')
			profile.first_name = form.cleaned_data.get('first_name')
			profile.last_name = form.cleaned_data.get('last_name')
			profile.location = form.cleaned_data.get('location')
			profile.url = form.cleaned_data.get('url')
			profile.profile_info = form.cleaned_data.get('profile_info')
			profile.save()
			return redirect('index')
	else:
		form = EditProfileForm()

	context = {
		'form':form,
	}

	return render(request, 'edit_profile.html', context)



@login_required
def follow(request, username, option):
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()

        return HttpResponseRedirect(reverse('profile', args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))
