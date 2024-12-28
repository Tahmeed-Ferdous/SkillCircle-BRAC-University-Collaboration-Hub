from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from dashboard.models import Tasks
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
import random

def dashboard(request):
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        task = request.POST.get('task')
        title = request.POST.get('title')
        img = request.FILES.get('img')
        # start_time, days
        
        if name and task and not title and not img:
            Tasks.objects.create(name=name, task=task)
            return redirect('dashboard')

        elif name and title and task and img:
            if Tasks.objects.filter(name=name).exists():
                error_message = "A user with this name already exists."
            else:
                Tasks.objects.create(name=name, title=title, task=task, img=img)
                return redirect('dashboard')

    tasks = Tasks.objects.exclude(name='', task='') 
    cards = Tasks.objects.exclude(title='', img='') 

    def extract_last_two_digits(task_obj):
        try:
            return int(task_obj.task[-2:])
        except (ValueError, AttributeError):
            return float('inf')

    sorted_tasks = sorted(tasks, key=extract_last_two_digits)
    return render(request, 'dashboard.html', {
        'tasks': sorted_tasks,
        'cards': cards,
        'error': error_message
    })
# routine planner views function to update the time table
def add_course(request):
    error_message=None
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time=request.POST.get('start_time')
        days=request.POST.get('days')
        if name and start_time and days:
            Tasks.objects.create(name=name, start_time=start_time, days=days)
            
            return redirect('dashboard')
# function to display added courses
from datetime import datetime

def displayOnSchedule(request):
    courses = Tasks.objects.all().exclude(start_time__isnull=True).exclude(days__isnull=True)
    timetable_data = {
        'Sunday': {},
        'Monday': {},
        'Tuesday': {},
        'Wednesday': {},
        'Thursday': {},
        'Friday': {},
        'Saturday': {}
    }

    for course in courses:
        days = course.days.split(',')
        for day in days:
            day = day.strip()
            if day in timetable_data:
                time_slot = course.start_time.strftime('%H:%M')
                if time_slot not in timetable_data[day]:
                    timetable_data[day][time_slot] = []
                timetable_data[day][time_slot].append(course.name)
    
    # Define proper time intervals
    time_slots = [
        ("08:00", "09:20"),
        ("09:30", "10:50"),
        ("11:00", "12:20"),
        ("12:30", "1:50"),
        ("2:00", "3:20"),
        ("3:30", "4:50"),
    ]
    

    return render(request, 'dashboard.html', {
        'timetable_data': timetable_data,
        'time_slots': time_slots
    })






def delete_task(request, task_id):
    task = Tasks.objects.get(id=task_id)
    task.delete()
    return redirect('dashboard')

def edit_task(request, id):
    task = get_object_or_404(Tasks, id=id)
    if request.method == 'POST':
        task.name = request.POST.get('name')
        task.task = request.POST.get('task')
        task.save()
        return redirect('dashboard')
    return render(request, 'edit.html', {'task': task})

from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages

def send_mail_req(request):
    templates = {
        'absent': "Dear {recipient_name},\n\nThis is to inform you about my absence from work.\n\nRegards,\n{sender_name}",
        'sick_leave': "Dear {recipient_name},\n\nI'm currently unwell and need sick leave.\n\nRegards,\n{sender_name}",
        'makeup_proposal': "Dear {recipient_name},\n\nHere’s a proposal for making up missed work.\n\nRegards,\n{sender_name}",
    }

    if request.method == 'POST':
        sender_email = request.POST.get('sender_email')
        recipient_email = request.POST.get('recipient_email') # No longer a select
        template_type = request.POST.get('template_type')

        if sender_email and recipient_email and template_type in templates:
            sender_name = sender_email.split('@')[0]
            recipient_name = recipient_email.split('@')[0]
            email_body = templates[template_type].format(recipient_name=recipient_name, sender_name=sender_name)
            email_subject = "Notification: " + template_type.replace('_', ' ').title()

            try:
                send_mail(
                    email_subject,
                    email_body,
                    sender_email,
                    [recipient_email],  # Still a list for send_mail
                    fail_silently=False,
                )
                messages.success(request, "Email sent successfully!")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")
        else:
            messages.error(request, "Invalid input. Please fill out the form correctly.")

    return render(request, 'dashboard.html') # No need to pass recipients
