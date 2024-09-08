from http.client import HTTPResponse

from django.conf.global_settings import LOGIN_REDIRECT_URL
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from app.models import Movie, Seat, Ticket


def list_movies(request):
    return render(request, 'app/movies.html', {
        'movies': Movie.objects.all()
    })


def list_seats(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    seats = Seat.objects.filter(ticket__seat=None)
    reserved_seats = Ticket.objects.filter(movie=movie).values_list('seat_id', flat=True)
    available_seats = Seat.objects.exclude(id__in=reserved_seats)
    return render(request, 'app/seats.html', {
        'movie': movie,
        'seats': available_seats
    })


def reserve_seat(request, movie_id, seat_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"/admin/login/?next=/movie/{movie_id}/seats")
    else:
        seat = get_object_or_404(Seat, id=seat_id)
        movie = get_object_or_404(Movie, id=movie_id)
        t= Ticket(seat = seat, movie=movie, user=request.user)
        t.save()
        return HttpResponseRedirect(f'/movie/{movie_id}/seats')


def stats(request):
    seats = Seat.objects.filter(ticket__seat__isnull=False).values('number').annotate(total=Count('ticket__seat'))
    response = list()
    for seat in seats:
        response.append({'seat__number':seat['number'],'total':seat['total']})
    return JsonResponse({'stats':response})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_movies')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
