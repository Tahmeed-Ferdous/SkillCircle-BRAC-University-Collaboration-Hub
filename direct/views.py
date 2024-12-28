from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from direct.models import Message


from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here.

from django.db import connection


@login_required
def Inbox(request):
    messages = Message.get_messages(user=request.user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        
        directs_query = """
            SELECT * 
            FROM direct_message 
            WHERE user_id = %s AND recipient_id = %s
        """
        directs = Message.objects.raw(directs_query, [request.user.id, message['user'].id])
        update_query = """
            UPDATE direct_message 
            SET is_read = TRUE 
            WHERE user_id = %s AND recipient_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(update_query, [request.user.id, message['user'].id])

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    return render(request, 'direct/direct.html', context)


@login_required
def Directs(request, username):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username

    # Use raw SQL to get the directs
    directs_query = """
        SELECT * 
        FROM direct_message 
        WHERE user_id = %s AND recipient_id = (SELECT id FROM auth_user WHERE username = %s)
    """
    directs = Message.objects.raw(directs_query, [user.id, username])

    # Mark the messages as read
    update_query = """
        UPDATE direct_message 
        SET is_read = TRUE 
        WHERE user_id = %s AND recipient_id = (SELECT id FROM auth_user WHERE username = %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(update_query, [user.id, username])

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    return render(request, 'direct/direct.html', context)


@login_required
def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user_query = """
            SELECT * 
            FROM auth_user 
            WHERE username = %s
        """
        to_user_result = User.objects.raw(to_user_query, [to_user_username])
        
        if not to_user_result:
            return HttpResponseBadRequest("User not found.")
        
        to_user = to_user_result[0]
        
        Message.send_message(from_user, to_user, body)
        return redirect('inbox')
    else:
        return HttpResponseBadRequest()


def checkDirects(request):
	directs_count = 0
	if request.user.is_authenticated:
		directs_count = Message.objects.filter(user=request.user, is_read=False).count()

	return {'directs_count':directs_count}

@login_required
def UserSearch(request):
	query = request.GET.get("q")
	context = {}
	
	if query:
		users = User.objects.filter(Q(username__icontains=query))

		#Pagination
		paginator = Paginator(users, 6)
		page_number = request.GET.get('page')
		users_paginator = paginator.get_page(page_number)

		context = {
				'users': users_paginator,
			}
	
	template = loader.get_template('direct/search_user.html')
	
	return HttpResponse(template.render(context, request))

@login_required
def NewConversation(request, username):
    from_user = request.user
    body = ''
    to_user_query = """
        SELECT * 
        FROM auth_user 
        WHERE username = %s
    """
    to_user_result = User.objects.raw(to_user_query, [username])
    
    if not to_user_result:
        return redirect('usersearch')
    
    to_user = to_user_result[0] 
    
    if from_user != to_user:
        Message.send_message(from_user, to_user, body)
        
    return redirect('inbox')
