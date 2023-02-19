from django.urls import path
import footerPages.views as footer_views

urlpatterns = [
    path('sell_fast', footer_views.sell_fast, name='sell_fast'),
    path('membership', footer_views.membership, name='membership'),
    path('banner', footer_views.banner, name='banner'),
    path('promote_ad', footer_views.promote_ad, name='promote_ad'),
    path('faq', footer_views.faq, name='faq'),
    path('stay_safe', footer_views.stay_safe, name='stay_safe'),
    path('contact_us', footer_views.contact_us, name='contact_us'),
    path('about_us', footer_views.about_us, name='about_us'),
    path('terms_cond', footer_views.terms_cond, name='terms_cond'),
    path('privacy', footer_views.privacy, name='privacy'),
]
