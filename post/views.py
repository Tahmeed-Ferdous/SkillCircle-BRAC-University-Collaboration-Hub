from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from post.models import Stream, Post, Tag, Likes
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from post.forms import NewPostForm
from authy.models import Profile
from django.urls import reverse
from authy.models import Profile

from comment.models import Comment
from comment.forms import CommentForm

@login_required
@never_cache
def index(request):
	user = request.user
	posts = Stream.objects.raw("SELECT * FROM post_stream WHERE user_id = %s", [user.id])

	group_ids = []

	for post in posts:
		group_ids.append(post.post_id)
		
	post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')		

	template = loader.get_template('index.html')

	context = {
		'post_items': post_items,

	}

	return HttpResponse(template.render(context, request))

def PostDetails(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	user = request.user
	profile = Profile.objects.raw("SELECT * FROM authy_profile WHERE user_id = %s", [user.id])
	favorited = False

    #comment
	comments = Comment.objects.filter(post=post).order_by('date')

	#Comments Form
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.user = user
			comment.save()
			return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
	else:
		form = CommentForm()
	
	if request.user.is_authenticated:
		profile = Profile.objects.raw("SELECT * FROM authy_profile WHERE user_id = %s", [user.id])[0]
		if profile.favorites.filter(id=post_id).exists():
			favorited = True
	template = loader.get_template('post_detail.html')
	context = {
		'post':post,
		'favorited':favorited,
		'form':form,
		'comments':comments,
	}
	return HttpResponse(template.render(context, request))

@login_required
def NewPost(request):
	user = request.user
	tags_objs = []
	files_objs = []

	if request.method == 'POST':
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			picture = form.cleaned_data.get('picture')
			caption = form.cleaned_data.get('caption')
			tags_form = form.cleaned_data.get('tags')

			tags_list = list(tags_form.split(','))

			for tag in tags_list:
				t, created = Tag.objects.get_or_create(title=tag)
				tags_objs.append(t)

			p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
			p.tags.set(tags_objs)
			p.save()
			return redirect('index')
	else:
		form = NewPostForm()

	context = {
		'form':form,
	}

	return render(request, 'newpost.html', context)


@login_required
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    tag_id = tag.id

    posts = Post.objects.raw(
        """
        SELECT post_post.* 
        FROM post_post
        INNER JOIN post_post_tags ON post_post.id = post_post_tags.post_id
        WHERE post_post_tags.tag_id = %s
        ORDER BY post_post.posted DESC
        """,
        [tag_id]
    )

    template = loader.get_template('tags.html')
    context = {
        'posts': posts,
        'tag': tag,
    }

    return HttpResponse(template.render(context, request))



@login_required
def like(request, post_id):
	user = request.user
	post = Post.objects.get(id=post_id)
	current_likes = post.likes
	liked = Likes.objects.filter(user=user, post=post).count()

	if not liked:
		like = Likes.objects.create(user=user, post=post)
		like.save()
		current_likes = current_likes + 1

	else:
		Likes.objects.filter(user=user, post=post).delete()
		current_likes = current_likes - 1

	post.likes = current_likes
	post.save()

	return HttpResponseRedirect(reverse('postdetails', args=[post_id]))


@login_required
def favorite(request, post_id):
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.raw("SELECT * FROM authy_profile WHERE user_id = %s", [request.user.id])[0]

    if profile.favorites.filter(id=post_id).exists():
        profile.favorites.remove(post)

    else:
        profile.favorites.add(post)

    return HttpResponseRedirect(reverse('postdetails', args=[post_id]))