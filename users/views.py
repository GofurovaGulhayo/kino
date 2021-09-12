from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import render, redirect
from django.views.generic import (ListView,  UpdateView, DeleteView)

from movie_finder.models import Movie
from .forms import ReviewForms
from .models import Review, MyRating


@login_required
def fill_form(request):
    imdb = request.GET.get('imdb', 'notSelected')
    if imdb == 'notSelected':
        messages.warning(request, f'URL Not Allowed. Select the movie first!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    movie = Movie.objects.get(imdb_id=imdb)

    if request.method == 'POST':
        form = ReviewForms(request.POST or None)
        if form.is_valid():
            form.instance.author = request.user
            form.instance.movie = movie
            form.save()

            messages.success(request, f'Added review for "{ movie.title }"')
            return redirect('movie-finder:result', imdb)
        else:
            print(form.errors)
    else:
        form = ReviewForms()

    params = {'form': form, 'movie': movie.title, 'imdb': imdb}
    return render(request, 'movie_finder/review.html', params)


@login_required
def add_rating(request):
    if request.method == 'POST':
        imdb = request.POST.get('imdb')
        if imdb[:6] != "delete":
            rating = request.POST.get('rating')

            movie = Movie.objects.get(imdb_id=imdb)

            if MyRating.objects.filter(movie=movie, user=request.user).exists():
                MyRating.objects.filter(movie=movie, user=request.user).update(rating=rating)
                return HttpResponse(status=204)
            else:
                MyRating(movie=movie, user=request.user, rating=rating).save()
                return HttpResponse(status=204)
        else:
            movie = Movie.objects.get(imdb_id=imdb[6:])
            try:
                delete_movie = MyRating.objects.get(movie=movie, user=request.user)
                messages.error(request, f'{movie.title} has been deleted from your rating!')
                delete_movie.delete()
            except MyRating.DoesNotExist:
                messages.error(request, f'Rating for {movie.title} does not exist!')

            return redirect(request.META['HTTP_REFERER'])

    return redirect(request.META['HTTP_REFERER'])


class PostListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'movie_finder/all-reviews.html'
    context_object_name = 'reviewPosts'
    ordering = ['-timestamp']
    paginate_by = 10


class PostListViewUser(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'movie_finder/my-reviews.html'
    context_object_name = 'reviewPosts'
    ordering = ['-timestamp']


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    context_object_name = 'reviews'
    fields = ['rating', 'review_description']
    template_name = 'movie_finder/review.html'
    success_url = '/movie-finder/reviews/'

    def form_valid(self, form, *args, **kwargs):
        form.instance.author = self.request.user
        messages.add_message(self.request, messages.INFO, f'Your review has been updated!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'movie_finder/confirm-delete.html'
    success_message = f"Review has been deleted successfully."
    success_url = '/movie-finder/reviews/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        messages.error(self.request, self.success_message)
        return super(PostDeleteView, self).delete(request, *args, **kwargs)
