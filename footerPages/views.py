from django.shortcuts import render
from django.shortcuts import redirect
import cx_Oracle

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='orcl')


# Create your views here.

def sell_fast(request):
    if request.session.has_key('username'):
        return render(request, 'sell_fast.html', {'username': request.session['username']})
    else:
        return render(request, 'sell_fast.html', {'username': ''})


def membership(request):
    if request.session.has_key('username'):
        return render(request, 'membership.html', {'username': request.session['username']})
    else:
        return render(request, 'membership.html', {'username': ''})


def banner(request):
    if request.session.has_key('username'):
        return render(request, 'banner.html', {'username': request.session['username']})
    else:
        return render(request, 'banner.html', {'username': ''})


def promote_ad(request):
    if request.session.has_key('username'):
        return render(request, 'promote_ad.html', {'username': request.session['username']})
    else:
        return render(request, 'promote_ad.html', {'username': ''})


def faq(request):
    if request.session.has_key('username'):
        return render(request, 'faq.html', {'username': request.session['username']})
    else:
        return render(request, 'faq.html', {'username': ''})


def stay_safe(request):
    if request.session.has_key('username'):
        return render(request, 'stay_safe.html', {'username': request.session['username']})
    else:
        return render(request, 'stay_safe.html', {'username': ''})


def contact_us(request):
    if request.session.has_key('username'):
        return render(request, 'contact_us.html', {'username': request.session['username']})
    else:
        return render(request, 'contact_us.html', {'username': ''})


def about_us(request):
    if request.session.has_key('username'):
        return render(request, 'about_us.html', {'username': request.session['username']})
    else:
        return render(request, 'about_us.html', {'username': ''})


def terms_cond(request):
    if request.session.has_key('username'):
        return render(request, 'terms_cond.html', {'username': request.session['username']})
    else:
        return render(request, 'terms_cond.html', {'username': ''})


def privacy(request):
    if request.session.has_key('username'):
        return render(request, 'privacy.html', {'username': request.session['username']})
    else:
        return render(request, 'privacy.html', {'username': ''})
