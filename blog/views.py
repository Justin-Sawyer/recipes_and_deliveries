from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect

from .models import Post, Category, Tag
from .forms import BlogPostForm, NewTagsForm, NewCategoriesForm, CommentForm

from random import shuffle


def blog_home(request):
    """ A view to return the blog home page """
    return render(request, 'blog/blog-home.html', {'community': True})


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

        # Sort blog articles by author
        if 'author' in request.GET:
            authors = request.GET['author'].split(',')
            posts = posts.filter(author_id__username__in=authors)
            authors = User.objects.filter(username__in=authors)

    current_sorting = f'{sort}_{direction}'

    template = 'blog/blog-articles.html'

    # Show 12 contacts per page.
    paginator = Paginator(posts, 12)
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
    """ A view to show an individual blog article, allow commenting
    and random other articles in side bar """
    comment_form = CommentForm
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        name = get_object_or_404(User, id=request.user.id)
        if name.is_superuser:
            name = "recipesanddeliveries"
        comment_form_temp = comment_form.save(commit=False)
        comment_form_temp.post = post
        comment_form_temp.name = name
        if comment_form.is_valid():
            comment_form.post = post
            comment_form.name = name
            comment_form.save()
            messages.success(request, 'Successfully added comment!')
            return HttpResponseRedirect(reverse(
                'article', args=[str(post_id)]))
        else:
            messages.error(request, 'It seems that your comment cannot \
                be posted. Sorry!')
            return HttpResponseRedirect(reverse(
                'article', args=[str(post_id)]))

    other_posts = list(Post.objects.exclude(id=post.id))
    shuffle(other_posts)

    context = {
        'post': post,
        'other_posts': other_posts,
        'comment_form': comment_form,
    }

    return render(request, 'blog/article.html', context)


@login_required
def add_post(request):
    """ Add a post to the blog """
    if request.method == 'POST':
        posts_form = BlogPostForm(request.POST, request.FILES)
        new_tag_form = NewTagsForm(request.POST)
        new_category_form = NewCategoriesForm(request.POST)
        if posts_form.is_valid():
            author = get_object_or_404(User, id=request.user.id)
            form_temp = posts_form.save(commit=False)
            form_temp.author = author

            # Check button for adding further posts
            add_more_posts = request.POST.getlist('add-more-posts')

            postsform = posts_form.save()
            new_post = Post.objects.get(id=postsform.id)

            # Handle new vs existing tags
            no_space_tags = True
            new_tags_form = NewTagsForm(request.POST)
            if new_tags_form.data['tagname']:
                new_tagname = new_tags_form.data['tagname']
                tagname_collection = Tag.objects.all()
                existing_tagname = Tag.objects.filter(tagname=new_tagname)
                if existing_tagname:
                    existing_tagname_id = tagname_collection.get(
                        id__in=existing_tagname)
                    new_post.tag.add(existing_tagname_id)
                if not existing_tagname:
                    if ' ' not in new_tagname:
                        new_tags_form.is_valid()
                        newtag = new_tags_form.save()
                        new_post.tag.add(newtag)
                        no_space_tags = True
                    else:
                        no_space_tags = False

            # Handle new vs exiting categories
            no_space_cats = True
            new_category_form = NewCategoriesForm(request.POST)
            if new_category_form.data['friendly_name']:
                new_category_name = new_category_form.data['friendly_name']
                category_collection = Category.objects.all()
                existing_category_name = (
                    Category.objects.filter(friendly_name=new_category_name))
                if existing_category_name:
                    existing_category_name_id = (
                        category_collection.get(id__in=existing_category_name))
                    new_post.category.add(existing_category_name_id)
                if not existing_category_name:
                    if ' ' not in new_category_name:
                        new_category_form.is_valid()
                        newcategory = new_category_form.save()
                        new_post.category.add(newcategory)
                        no_space_cats = True
                    else:
                        no_space_cats = False

            if no_space_tags and no_space_cats:
                messages.success(request, 'Successfully added post!')
            else:
                messages.warning(request, 'Your post was added, but we were not able \
                    to add your tags and/or categories. Please add these one \
                    word at a time!')
                return redirect(reverse('edit_post', args=[postsform.id]))

            # Handle redirect according to whether
            # Further Posts is checked or not
            if add_more_posts:
                return redirect(reverse('add_post'))
            else:
                return redirect(reverse('blog-articles'))
        else:
            messages.error(request, 'Failed to add your post \
                Please ensure the form is valid.')
    else:
        new_category_form = NewCategoriesForm
        new_tag_form = NewTagsForm
        posts_form = BlogPostForm

    template = 'blog/add_post.html'

    context = {
        'posts_form': posts_form,
        'new_tag_form': new_tag_form,
        'new_category_form': new_category_form,
    }

    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """ Edit a blog post """
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author or request.user.is_superuser:
        new_category_form = NewCategoriesForm
        new_tag_form = NewTagsForm
        if request.method == 'POST':
            new_tag_form = NewTagsForm(request.POST)
            new_category_form = NewCategoriesForm(request.POST)
            posts_form = BlogPostForm(request.POST,
                                      request.FILES,
                                      instance=post)
            
            # Check button for adding further tags or categories
            add_more_tags = request.POST.getlist('add-more-tags')
            add_more_cats = request.POST.getlist('add-more-cats')

            if posts_form.is_valid():
                postsform = posts_form.save()
                new_post = Post.objects.get(id=postsform.id)

                no_space_tags = True
                new_tags_form = NewTagsForm(request.POST)
                if new_tags_form.data['tagname']:
                    new_tagname = new_tags_form.data['tagname']
                    tagname_collection = Tag.objects.all()
                    existing_tagname = Tag.objects.filter(tagname=new_tagname)
                    if existing_tagname:
                        existing_tagname_id = (
                            tagname_collection.get(id__in=existing_tagname))
                        new_post.tag.add(existing_tagname_id)
                    if not existing_tagname:
                        if ' ' not in new_tagname:
                            new_tags_form.is_valid()
                            newtag = new_tags_form.save()
                            new_post.tag.add(newtag)
                            no_space_tags = True
                        else:
                            no_space_tags = False

                no_space_cats = True
                new_category_form = NewCategoriesForm(request.POST)
                if new_category_form.data['friendly_name']:
                    new_category_name = new_category_form.data['friendly_name']
                    category_collection = Category.objects.all()
                    existing_category_name = (
                        Category.objects.filter(
                            friendly_name=new_category_name))
                    if existing_category_name:
                        existing_category_name_id = (
                            category_collection.get(
                                id__in=existing_category_name))
                        new_post.category.add(existing_category_name_id)
                    if not existing_category_name:
                        if ' ' not in new_category_name:
                            new_category_form.is_valid()
                            newcategory = new_category_form.save()
                            new_post.category.add(newcategory)
                            no_space_cats = True
                        else:
                            no_space_cats = False
                if not no_space_cats and not no_space_tags:
                    messages.warning(request, 'Your post was added, but we were not able \
                        to add your categories and/or tags. Please add these \
                        one word at a time!')
                    return redirect(reverse('edit_post', args=[postsform.id]))
                elif no_space_cats and not no_space_tags:
                    messages.warning(request, 'Your post was added, but we were not able \
                        to add your tags. Please add these \
                        one word at a time!')
                    return redirect(reverse('edit_post', args=[postsform.id]))
                elif no_space_tags and not no_space_cats:
                    messages.warning(request, 'Your post was added, but we were not able \
                        to add your categories. Please add these \
                        one word at a time!')
                    return redirect(reverse('edit_post', args=[postsform.id]))
                elif add_more_tags or add_more_cats:
                    messages.warning(request, 'Your tag/category was added. \
                        You can now add another')
                    return redirect(reverse('edit_post', args=[postsform.id]))
                else:
                    messages.success(request, 'Successfully updated post!')
                    return redirect(reverse('article', args=[post.id]))
            else:
                messages.error(request, 'Failed to edit post \
                    Please ensure the form is valid.')
        else:
            new_category_form = NewCategoriesForm
            new_tag_form = NewTagsForm
            posts_form = BlogPostForm(instance=post)
    else:
        messages.error(request, 'Sorry, only the post author can do that!')
        return redirect(reverse('home'))

    template = 'blog/edit_post.html'
    context = {
        'posts_form': posts_form,
        'new_tag_form': new_tag_form,
        'new_category_form': new_category_form,
        'post': post,
        'edit_article': True,
    }

    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """ Delete a blog post """
    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.author or request.user.is_superuser:
        post.delete()
        messages.success(request, 'Post successfully deleted!')
        return redirect(reverse('blog-articles'))
    else:
        messages.error(request, 'Sorry, only post authors can do that!')
        return redirect(reverse('home'))
