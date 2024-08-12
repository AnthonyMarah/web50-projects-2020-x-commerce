from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.contrib import messages


def index(request):
    listings = AuctionListing.objects.filter(active=True)
    won_listings = []
    
   
    if request.user.is_authenticated:
        won_listings = Bid.objects.filter(bidder=request.user, listing__active=False)

    return render(request, 'auctions/index.html', {'listings': listings, 'won_listings': won_listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.current_bid = listing.starting_bid
            listing.save()
            return redirect('index')  # Redirect to a page showing all listings or the newly created listing
    else:
        form = AuctionListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})

@login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    is_in_watchlist = request.user.is_authenticated and Watchlist.objects.filter(user=request.user, listing=listing).exists()
    comments = Comment.objects.filter(listing=listing)

    bid_form = BidForm()
    comment_form = CommentForm()
    highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()

    if request.method == 'POST':
        if 'bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data['bid_amount']
                if listing.current_bid is None:
                    listing.current_bid = listing.starting_bid
                if bid_amount > listing.current_bid:
                    Bid.objects.create(listing=listing, bidder=request.user, bid_amount=bid_amount)
                    listing.current_bid = bid_amount
                    listing.save()
                    messages.success(request, 'Your bid was placed successfully.')
                    return redirect('listing_detail', listing_id=listing.id)
                else:
                    messages.error(request, 'Your bid must be higher than the current bid.')
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                Comment.objects.create(listing=listing, commenter=request.user, comment_text=comment_form.cleaned_data['comment_text'])
                messages.success(request, 'Your comment was added successfully.')
        elif 'close_auction' in request.POST and listing.created_by == request.user:
            listing.active = False
            listing.save()
            messages.success(request, 'The auction has been closed.')
            return redirect('listing_detail', listing_id=listing.id)

    context = {
        'listing': listing,
        'is_in_watchlist': is_in_watchlist,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': comments,
        'highest_bid': highest_bid,
    }
    return render(request, 'auctions/listing_detail.html', context)


@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    Watchlist.objects.get_or_create(user=request.user, listing=listing)
    return redirect('listing_detail', listing_id=listing.id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    Watchlist.objects.filter(user=request.user, listing=listing).delete()
    return redirect('listing_detail', listing_id=listing.id)

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    if listing.created_by == request.user:
        listing.active = False
        listing.save()
        messages.success(request, 'The auction has been closed.')
    return redirect('listing_detail', listing_id=listing.id)

@login_required
def watchlist(request):
    # Get all listings in the user's watchlist
    watchlist_items = Watchlist.objects.filter(user=request.user)
    listings = [item.listing for item in watchlist_items]
    return render(request, 'auctions/watchlist.html', {'listings': listings})

def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories_list.html', {'categories': categories})

def category_listings(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = AuctionListing.objects.filter(category=category, active=True)
    return render(request, 'auctions/category_listings.html', {'category': category, 'listings': listings})