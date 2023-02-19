from django.urls import path
import my_account.views as my_acc_views

urlpatterns = [
    path('my_account_page', my_acc_views.my_account_page, name='my_account_page'),
    path('setup_membership', my_acc_views.setup_membership, name='setup_membership'),
    path('request_membership', my_acc_views.request_membership, name='request_membership'),
    path('my_membership_page', my_acc_views.my_membership_page, name='my_membership_page'),
    path('save_fav', my_acc_views.save_fav, name='save_fav'),
    path('del_fav', my_acc_views.del_fav, name='del_fav'),
    path('favourites', my_acc_views.favourites, name='favourites'),
    path('settings', my_acc_views.settings, name='settings'),
    path('post_ad_func', my_acc_views.post_ad_func, name='post_ad_func'),
    path('post_ad', my_acc_views.post_ad, name='post_ad'),
    path('ad_promotion_redirect', my_acc_views.ad_promotion_redirect, name='ad_promotion_redirect'),
    path('ad_promotion', my_acc_views.ad_promotion, name='ad_promotion'),
    path('reqest_ad_promotion', my_acc_views.reqest_ad_promotion, name='reqest_ad_promotion'),
    path('chat', my_acc_views.chat, name='chat'),
    path('open_chat_box', my_acc_views.open_chat_box, name='open_chat_box'),
    path('chat_box_redirect', my_acc_views.chat_box_redirect, name='chat_box_redirect'),
    path('chat_box', my_acc_views.chat_box, name='chat_box'),
    path('get_last_text', my_acc_views.get_last_text, name='get_last_text'),
    path('update_user_info', my_acc_views.update_user_info, name='update_user_info'),
    path('update_user_password', my_acc_views.update_user_password, name='update_user_password'),
]
