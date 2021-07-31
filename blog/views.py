from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower

from .models import Post, Category, Tag
from .forms import BlogPostForm, NewTagsForm
from profiles.models import UserProfile
from django.contrib.auth.models import User


def blog_home(request):
    """ A view to return the blog home page """
    return render(request, 'blog/blog-home.html')


def all_blog_articles(request):
    """ A view to return all blog articles """
    posts = Post.objects.all().order_by('-pk')
    authors = None
    categories = None
    tags = None
    sort = None
    direction = None
    query = None

    if request.GET:
        # Sort products via the dropdown menu
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'title':
                sortkey = 'lower_title'
                posts = posts.annotate(lower_title=Lower('title'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            posts = posts.order_by(sortkey)

        # Sort blog articles by category
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            posts = posts.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        # Sort blog articles by tag
        if 'tag' in request.GET:
            tags = request.GET['tag'].split(',')
            posts = posts.filter(tag__tagname__in=tags)
            tags = Tag.objects.filter(tagname__in=tags)

        if 'author' in request.GET:
            authors = request.GET['author'].split(',')
            posts = posts.filter(author_id__username__in=authors)
            authors = User.objects.filter(username__in=authors)

    current_sorting = f'{sort}_{direction}'

    template = 'blog/blog-articles.html'

    paginator = Paginator(posts, 12)  # Show 12 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'search_term': query,
        'current_categories': categories,
        'current_tags': tags,
        'current_sorting': current_sorting,
        'current_authors': authors,
        'page_obj': page_obj,
        'is_paginated': True,
    }
    return render(request, template, context)


def article(request, post_id):
    """ A view to show an individual blog article """
    post = get_object_or_404(Post, pk=post_id)

    context = {
        'post': post
    }

    return render(request, 'blog/article.html', context)


@login_required
def add_post(request):
    """ Add a product to the store """
    """if not request.user.is_superuser:
        messages.error(request, 'Sorry, only storeowners can do that!')
        return redirect(reverse('home'))"""

    """ Gets username as author """
    if request.method == 'POST':
        author = get_object_or_404(User, id=request.user.id)
        new_tag_form = NewTagsForm(request.POST)
        form = BlogPostForm(request.POST, request.FILES)
        form_temp = form.save(commit=False)
        form_temp.author = author
        # Check button for adding further posts
        add_more_posts = request.POST.getlist('add-more-posts')
        print(request.POST)
        if form.is_valid() and new_tag_form.is_valid():
            form_temp = form.save(commit=False)
            new_tag = new_tag_form.save()
            # tagname = Post.objects.create(new_tag)
            # form_temp.tag.add(tagname)
            #print(new_tag)
            print(new_tag.id)
            newtag = new_tag.id
            print(newtag)
            #new_tag_id = Tag.objects.get(id=new_tag.id)
            #print(new_tag_id)
            # form_temp.tag = new_tag_form
            # new_tag = request.new_tag_form.get("tagname")
            # new_tag = get_object_or_404(Tag, id=request.tagname)
            # form_temp.tag.add(new_tag.id)
            # print(form_temp.tag)
            # form.tag.add(newtag)
            saved_form = form.save()
            saved_form.tag.add(newtag)
            messages.info(request, 'Successfully added post!')
            if add_more_posts:
                return redirect(reverse('add_post'))
            else:
                return redirect(reverse('blog-articles'))
        else:
            messages.error(request, 'Failed to add product \
                Please ensure the form is valid.')
    else:
        new_tag_form = NewTagsForm
        form = BlogPostForm
    template = 'blog/add_post.html'
    context = {
        'form': form,
        'new_tag_form': new_tag_form,
    }

    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """ Edit a product in the store """
    """if not request.user.is_superuser:
        messages.error(request, 'Sorry, only storeowners can do that!')
        return redirect(reverse('home'))"""

    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated post!')
            return redirect(reverse('article', args=[post.id]))
            # return redirect(reverse('home'))
        else:
            messages.error(request, 'Failed to edit post \
                Please ensure the form is valid.')
    else:
        form = BlogPostForm(instance=post)
        messages.warning(request, f'You are editing {post.title}')

    template = 'blog/edit_post.html'
    context = {
        'form': form,
        'post': post,
        'edit_article': True,
    }

    return render(request, template, context)
