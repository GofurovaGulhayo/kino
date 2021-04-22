import wikipedia as wk
import json

from django.shortcuts import render
from urllib.request import urlopen
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

API_KEY = settings.API_KEY


#  function to find user's IP location, by default return user IP
#       'ip' - represents, that it's user's IP address
def find_ip_address(ip=''):
    try:
        response = urlopen("http://ipwhois.app/json/" + ip)

        # return JSON with details about IP address
        return json.load(response)
    except:
        return find_ip_address()  # send details about user's address only


# function to create a link to Wikipedia by keyword
def get_url(keyword):
    links = wk.search(keyword)  # search keyword in Wiki
    page = wk.page(links[0])  # take 1st result
    return page.url


# function for generating a Map URL to be embedded in a website.
#   lat - latitude
#   lng - longitude
def get_map_url(lat, lng):
    try:
        print(f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q={lat},{lng}&maptype=satellite&zoom=20')
        return f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q={lat},{lng}&maptype=satellite&zoom=20'
    except:
        return f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q='


# function to render template's html and data
@csrf_exempt
def index(request):
    if 'ip_address' in request.GET:  # fetching IP address from template
        data = find_ip_address(request.GET['ip_address'])  # if user enters data than it'll find it's IP details
    else:
        data = find_ip_address()  # if IP field is empty, it'll return user's address
    try:
        map_url = get_map_url(data['latitude'], data['longitude'])  # try to fetch URL for MAP using lat, lng fetched from IP
        page_link = get_url(f"{data['city']} in {data['country']}")  # fetching wikipedia page link
    except:
        map_url = f'https://www.maps.google.com'
        page_link = 'https://www.wikipedia.org'

    return render(request, "ip-locator/ip-locator.html",
                  {'data': data, 'page_link': page_link, 'map_url': map_url})
