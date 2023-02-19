from django.urls import path
import BikroyHome.views as home_views

urlpatterns = [
    path('', home_views.home, name='host'),
    path('home', home_views.home, name='home'),
    path('register_form', home_views.register_form, name='register_form'),
    path('register', home_views.register, name='register'),
    path('login', home_views.login, name='login'),
    path('signout', home_views.signout, name='signout'),
    path('all_ads', home_views.all_ads, name='all_ads'),
    path('get_ad', home_views.get_ad, name='get_ad'),
    path('view_ad', home_views.view_ad, name='view_ad'),
    path('reporting_ad', home_views.reporting_ad, name='reporting_ad'),
    path('verify_pass', home_views.verify_pass, name='verify_pass'),
    path('delete_post',home_views.delete_post,name ='delete_post')
]
