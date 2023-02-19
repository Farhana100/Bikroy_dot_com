from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files.storage import default_storage
import cx_Oracle

from django.contrib.auth.hashers import make_password, check_password

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='orcl')


# Create your views here.


def my_account_page(request):
    if not request.session.has_key('username'):
        return redirect('login')

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_PHONE_NUM WHERE POSTER_ID = %s AND PRODUCT_AD_ID = PROD_IMAGE_ID AND PRODUCT_AD_ID = PROD_PHONE_ID AND APPROVER_ID IS NULL ORDER BY TIME_OF_POST DESC"
    cur.execute(statement % request.session['user_id'])
    my_pending_ads = cur.fetchall()

    statement = "SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_PHONE_NUM WHERE POSTER_ID = %s AND PRODUCT_AD_ID = PROD_IMAGE_ID AND PRODUCT_AD_ID = PROD_PHONE_ID AND APPROVER_ID IS NOT NULL ORDER BY TIME_OF_POST DESC"
    cur.execute(statement % request.session['user_id'])
    my_ads = cur.fetchall()

    cur.close()
    connection.close()

    dict = {
        'my_pending_ads': my_pending_ads,
        'my_ads': my_ads,
        'username': request.session['username'],
        'email': request.session['email']
    }

    if request.session.has_key('ad_prom_msg'):
        dict['ad_prom_msg'] = request.session['ad_prom_msg']
        del(request.session['ad_prom_msg'])

    return render(request, 'my_account_page.html', dict)


def my_membership_page(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = (
        "SELECT MEMBERSHIP_TYPE, MEMBERSHIP_DATE, ADD_MONTHS(MEMBERSHIP_DATE, DURATION) EXP_DATE,  (ADD_MONTHS(MEMBERSHIP_DATE, DURATION) - SYSDATE) TIME_LEFT, PAYMENT_SATUS "
        "FROM MEMBER WHERE MEMBER_ID = %s")
    cur.execute(statement % request.session['user_id'])
    is_member = cur.fetchall()
    cur.close()
    connection.close()

    dict = {
        'username': request.session['username'],
        'user_id': request.session['user_id'],
        'email': request.session['email'],
        'is_member': False
    }

    if is_member:
        mem_type, mem_date, exp_date, time_left, payment_stat = is_member[0]

        if mem_type == 'A':
            mem_type = '1 month plan'
        elif mem_type == 'B':
            mem_type = '6 months plan'
        else:
            mem_type = '1 year plan'

        dict['mem_type'] = mem_type
        dict['mem_date'] = mem_date
        dict['exp_date'] = exp_date
        dict['time_left'] = int(time_left)
        dict['payment_stat'] = payment_stat
        dict['is_member'] = is_member

    return render(request, 'my_membership_page.html', dict)


def request_membership(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT MEMBERSHIP_TYPE FROM MEMBER WHERE MEMBER_ID = %s"
    cur.execute(statement % request.session['user_id'])
    is_member = cur.fetchall()

    cur.close()
    connection.close()

    dict = {'username': request.session['username'], 'user_id': request.session['user_id'],
            'email': request.session['email'], 'is_member': is_member}
    return render(request, 'request_membership.html', dict)


def setup_membership(request):
    chosen_mem_type = request.POST['chosen_mem_type']

    if chosen_mem_type == 'one_month':
        mem_type = 'A'
    elif chosen_mem_type == 'six_months':
        mem_type = 'B'
    else:
        mem_type = 'C'

    if chosen_mem_type == 'one_month':
        duration = 1
    elif chosen_mem_type == 'six_months':
        duration = 6
    else:
        duration = 12

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "INSERT INTO MEMBER VALUES(%s,'%s', SYSDATE, %s, 'N')"

    cur.execute(statement % (request.session['user_id'], mem_type, duration))

    cur.close()
    connection.commit()
    connection.close()

    return redirect('my_membership_page')


def favourites(request):
    if not request.session.has_key('user_id'):
        redirect('login')

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                 "AND PRODUCT_AD_ID = ANY( "
                 "SELECT FAV_AD_ID FROM FAVOURITE WHERE FAV_USER_ID = %s ) "
                 "ORDER BY TIME_OF_POST")
    cur.execute(statement % (request.session['user_id']))

    fav_ads = cur.fetchall();

    cur.close()
    connection.close()

    dict = {
        'fav_ads': fav_ads,
        'username': request.session['username'],
        'email': request.session['email']
    }

    return render(request, 'favourites.html', dict)


def settings(request):
    city_loc = []
    div_loc = []
    city_sub_loc = {}
    div_sub_loc = {}

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT LOCATION_ID, LOCATION_NAME FROM LOCATIONS WHERE PARENT_ID IS NULL"
    cur.execute(statement)
    result = cur.fetchall()

    for loc in result:
        nam = str(loc[1])
        statement = "SELECT LOCATION_NAME FROM LOCATIONS WHERE PARENT_ID ='%s'"
        cur.execute(statement % str(loc[0]))
        res = cur.fetchall()
        if nam.lower().__contains__('division'):
            div_loc.append(nam)
            subloc = []
            for sub in res:
                subloc.append(sub[0])
            div_sub_loc[nam] = subloc
        else:
            city_loc.append(nam)
            subloc = []
            for sub in res:
                subloc.append(sub[0])
            city_sub_loc[nam] = subloc

    cat = []
    sub_cat = {}

    statement = " SELECT CATEGORY_ID,CATEGORY_NAME FROM CATEGORIES WHERE PARENT_ID IS NULL"
    cur.execute(statement)
    result = cur.fetchall()
    for ct in result:
        cat.append(ct[1])
        statement = "SELECT CATEGORY_NAME FROM CATEGORIES WHERE PARENT_ID ='%s'"
        cur.execute(statement % str(ct[0]))
        res = cur.fetchall()
        subcat = []
        for sub in res:
            subcat.append(sub[0])
        sub_cat[str(ct[1])] = subcat

    dict = {
        'city_loc': city_loc,
        'div_loc': div_loc,
        'city_sub_loc': city_sub_loc,
        'div_sub_loc': div_sub_loc,
        'cat': cat,
        'sub_cat': sub_cat
    }

    email = request.session['email']

    statement = "SELECT * FROM USER_ WHERE EMAIL_ADDR = '%s'"

    cur.execute(statement % email)
    result = cur.fetchall()
    cur.close()
    connection.close()

    _, username, _, _, _, location, sublocation, _ = result[0]

    dict['username'] = username
    dict['email'] = email
    dict['location'] = location
    dict['sublocation'] = sublocation

    if request.session.has_key('sm_msg'):
        dict['sm_msg'] = request.session['sm_msg']
        dict['msg'] = ''
        del (request.session['sm_msg'])
        return render(request, 'settings.html', dict)
    elif request.session.has_key('msg'):
        dict['msg'] = request.session['msg']
        dict['sm_msg'] = ''
        del (request.session['msg'])
        return render(request, 'settings.html', dict)
    else:
        dict['msg'] = ''
        dict['sm_msg'] = ''
        return render(request, 'settings.html', dict)


def update_user_password(request):
    Current_Pass = request.POST['Current_Pass']
    New_Pass = request.POST['New_Pass']
    Confirm_New_Pass = request.POST['Confirm_New_Pass']
    email = request.session['email']

    statement = "SELECT PASSWORD FROM USER_ WHERE EMAIL_ADDR = '%s'"

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement % email)
    temp = cur.fetchall()
    hashed_pass, = temp[0]
    cur.close()
    connection.close()

    if not check_password(Current_Pass, hashed_pass):
        request.session['sm_msg'] = "Incorrect Current Password"
        return redirect('settings')

    if not New_Pass == Confirm_New_Pass:
        request.session['sm_msg'] = "New Passwords don't match"
        return redirect('settings')

    New_Pass = make_password(New_Pass)

    statement = "UPDATE USER_ SET PASSWORD = '%s' WHERE EMAIL_ADDR = '%s'"

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement % (New_Pass, email))
    cur.close()
    connection.commit()
    connection.close()

    request.session['msg'] = "Password updated successfully"
    return redirect('settings')


def update_user_info(request):
    new_name = request.POST['new_name']
    new_loc = request.POST['new_loc']
    new_subloc = request.POST['new_subloc']
    email = request.session['email']

    statement = "UPDATE USER_ SET NAME = '" + new_name + "', LOCATION = '" + new_loc + "', SUB_LOCATION = '" + new_subloc + "'" + "WHERE EMAIL_ADDR = '" + email + "'"

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement)

    cur.close()
    connection.commit()
    connection.close()

    request.session['msg'] = "Information updated successfully"
    return redirect('settings')


def post_ad_func(request):
    title = str(request.POST['title'])
    description = str(request.POST['description'])
    price = int(request.POST['price'])
    is_nego = str(request.POST.get('is_nego', False))
    condition = str(request.POST['condition'])
    new_cat = str(request.POST['new_cat'])
    new_subcat = str(request.POST['new_subcat'])
    new_loc = str(request.POST['new_loc'])
    new_subloc = str(request.POST['new_subloc'])

    img1 = request.FILES['img1']
    phone_number1 = int(request.POST['phone_number1'])

    user_id = int(request.session['user_id'])
    email = str(request.session['email'])

    statement = "SELECT MAX(PRODUCT_AD_ID) FROM PRODUCT_AD"

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement)
    result, = cur.fetchall()[0]

    if result is None:
        result = 0
    post_id = result + 1
    img1_name = str(post_id) + "_" + email + "." + img1.name.split(".")[-1]

    is_nego = 'N' if is_nego == 'False' else 'Y'

    statement = "INSERT INTO PRODUCT_AD(PRODUCT_AD_ID, TITLE, DESCRIPTION, TIME_OF_POST, PRICE, NEGOTIABLE, CONDITION, CATEGORY, SUB_CATEGORY, LOCATION, SUB_LOCATION, POSTER_ID) VALUES(%s, q'[%s]',q'[%s]', SYSDATE,'%s','%s','%s','%s','%s', '%s', '%s', %s)"
    cur.execute(statement % (
        post_id, title, description, price, is_nego, condition, new_cat, new_subcat, new_loc, new_subloc, user_id))

    statement = "INSERT INTO PROD_IMAGE(PROD_IMAGE_ID, IMAGE) VALUES (%s, '%s')"
    cur.execute(statement % (post_id, img1_name))

    statement = "INSERT INTO PROD_PHONE_NUM(PROD_PHONE_ID, PHONE_NUM) VALUES (%s, %s)"
    cur.execute(statement % (post_id, phone_number1))

    statement = "INSERT INTO PROD_AD_TYPE(PROD_TYPE_ID, AD_TYPE) VALUES (%s, 'normal')"
    cur.execute(statement % post_id)

    cur.close()
    connection.commit()
    connection.close()

    # storing image file
    default_storage.save(img1_name, img1)

    return redirect('my_account_page')


def post_ad(request):
    if not request.session.has_key('username'):
        return redirect('login')

    email = request.session['email']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT POSTS_ALLOWANCE(%s) FROM DUAL"
    cur.execute(statement % request.session['user_id'])

    posts_left, = cur.fetchall()[0]

    city_loc = []
    div_loc = []
    city_sub_loc = {}
    div_sub_loc = {}

    statement = "SELECT LOCATION_ID, LOCATION_NAME FROM LOCATIONS WHERE PARENT_ID IS NULL"
    cur.execute(statement)
    result = cur.fetchall()

    for loc in result:
        nam = str(loc[1])
        statement = "SELECT LOCATION_NAME FROM LOCATIONS WHERE PARENT_ID ='%s'"
        cur.execute(statement % str(loc[0]))
        res = cur.fetchall()
        if nam.lower().__contains__('division'):
            div_loc.append(nam)
            subloc = []
            for sub in res:
                subloc.append(sub[0])
            div_sub_loc[nam] = subloc
        else:
            city_loc.append(nam)
            subloc = []
            for sub in res:
                subloc.append(sub[0])
            city_sub_loc[nam] = subloc

    cat = []
    sub_cat = {}

    statement = " SELECT CATEGORY_ID,CATEGORY_NAME FROM CATEGORIES WHERE PARENT_ID IS NULL"
    cur.execute(statement)
    result = cur.fetchall()
    for ct in result:
        cat.append(ct[1])
        statement = "SELECT CATEGORY_NAME FROM CATEGORIES WHERE PARENT_ID ='%s'"
        cur.execute(statement % str(ct[0]))
        res = cur.fetchall()
        subcat = []
        for sub in res:
            subcat.append(sub[0])
        sub_cat[str(ct[1])] = subcat

    cur.close()
    connection.close()

    dict = {
        'city_loc': city_loc,
        'div_loc': div_loc,
        'city_sub_loc': city_sub_loc,
        'div_sub_loc': div_sub_loc,
        'cat': cat,
        'sub_cat': sub_cat,
        'posts_left': posts_left,
        'username': request.session['username'],
        'email': request.session['email']
    }
    return render(request, 'post_ad.html', dict)


def ad_promotion_redirect(request):
    request.session['promote_post_id'] = request.POST['post_id']
    return redirect('ad_promotion')


def ad_promotion(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT IS_MEMBER(%s) FROM DUAL"
    cur.execute(statement % request.session['user_id'])
    is_member = cur.fetchall()

    cur.close()
    connection.close()

    dict = {
        'username': request.session['username'],
        'user_id': request.session['user_id'],
        'email': request.session['email'],
        'is_member': is_member
    }

    return render(request, 'promote_my_ad.html', dict)


def reqest_ad_promotion(request):
    urgent = request.POST.get('urgent', False)
    top = request.POST.get('top', False)
    spot = request.POST.get('spot', False)

    type = "update"

    if urgent:
        type += "-" + urgent

    if top:
        type += "-" + top

    if spot:
        type += "-" + spot

    if request.session.has_key('promote_post_id'):
        promote_post_id = request.session['promote_post_id']
        del (request.session['promote_post_id'])

        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()

        statement = "UPDATE PROD_AD_TYPE SET AD_TYPE = '%s' WHERE PROD_TYPE_ID = %s"
        cur.execute(statement % (type, promote_post_id))
        request.session['ad_prom_msg'] = 'Your Ad promotion request has been send to the admin. We will soon contact ' \
                                         'you for the payment vis email or contact number. Thank you.'

        cur.close()
        connection.commit()
        connection.close()

    return redirect('my_account_page')


def save_fav(request):
    fav_post_id = request.POST['fav_post_id']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "INSERT INTO FAVOURITE VALUES(%s, %s)"

    cur.execute(statement % (fav_post_id, request.session['user_id']))

    cur.close()
    connection.commit()
    connection.close()

    return redirect('view_ad')


def del_fav(request):
    fav_post_id = request.POST['fav_post_id']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "DELETE FROM FAVOURITE WHERE FAV_AD_ID = %s AND FAV_USER_ID = %s"
    cur.execute(statement % (fav_post_id, request.session['user_id']))

    cur.close()
    connection.commit()
    connection.close()

    return redirect('view_ad')


def chat(request):
    if not request.session.has_key('username'):
        return redirect('login')

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT A.TEXT, A.TIME, A.SENDER_ID, A.RECEIVER_ID, NAME "
                 "FROM MESSAGE A, USER_ "
                 "WHERE (A.RECEIVER_ID = %s OR A.SENDER_ID = %s) "
                 "AND ((USER_ID = A.RECEIVER_ID AND A.SENDER_ID = %s) OR (USER_ID = A.SENDER_ID AND A.RECEIVER_ID = %s)) "
                 "AND NOT EXISTS( "
                 "SELECT * FROM MESSAGE B "
                 "WHERE A.TIME < B.TIME "
                 "AND ((A.RECEIVER_ID = B.RECEIVER_ID AND A.SENDER_ID = B.SENDER_ID) OR (A.RECEIVER_ID = B.SENDER_ID AND A.SENDER_ID = B.RECEIVER_ID)) "
                 ")")
    cur.execute(statement % (
        request.session['user_id'], request.session['user_id'], request.session['user_id'], request.session['user_id']))
    msg_list = cur.fetchall()

    cur.close()
    connection.close()

    dict = {'msg_list': msg_list,
            'username': request.session['username'],
            'user_id': request.session['user_id']}

    return render(request, 'chat_page.html', dict)


def open_chat_box(request):
    if not request.session.has_key('username'):
        return redirect('login')

    poster_id = request.POST.get('poster_id', False)
    poster_name = request.POST.get('poster_name', False)
    msg = request.POST.get('msg', False)

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT COUNT(*) FROM MESSAGE"
    cur.execute(statement)
    msg_id, = cur.fetchall()[0]
    msg_id += 1

    statement = "INSERT INTO MESSAGE VALUES(%s, '%s', SYSDATE, %s, %s)"
    cur.execute(statement % (msg_id, msg, request.session['user_id'], poster_id))

    cur.close()
    connection.commit()
    connection.close()

    request.session['receiver_id'] = poster_id
    request.session['receiver_name'] = poster_name

    return redirect('chat_box')


def chat_box_redirect(request):
    request.session['receiver_id'] = request.POST['receiver_id']
    request.session['receiver_name'] = request.POST['receiver_name']
    return redirect('chat_box')


def chat_box(request):
    sender_id = request.session['user_id']
    receiver_id = request.session['receiver_id']
    receiver_name = request.session['receiver_name']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT * FROM ( "
                 "SELECT * FROM MESSAGE "
                 "WHERE (SENDER_ID = %s "
                 "OR SENDER_ID = %s) "
                 "AND (RECEIVER_ID = %s "
                 "OR RECEIVER_ID = %s) "
                 "ORDER BY TIME DESC "
                 ") top_10_prod "
                 "WHERE rownum <= 10 ORDER BY rownum DESC")

    cur.execute(statement % (sender_id, receiver_id, receiver_id, sender_id))
    messages = cur.fetchall()

    cur.close()
    connection.close()

    dict = {
        'username': request.session['username'],
        'user_id': request.session['user_id'],
        'receiver_id': receiver_id,
        'receiver_name': receiver_name,
        'messages': messages
    }

    return render(request, 'chat_box_page.html', dict)


def get_last_text(request):
    sender_id = request.session['user_id']
    receiver_id = request.session['receiver_id']
    receiver_name = request.session['receiver_name']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT * FROM ( "
                 "SELECT * FROM MESSAGE "
                 "WHERE (SENDER_ID = %s "
                 "OR SENDER_ID = %s) "
                 "AND (RECEIVER_ID = %s "
                 "OR RECEIVER_ID = %s) "
                 "ORDER BY TIME DESC "
                 ") top_10_prod "
                 "WHERE rownum <= 10 ORDER BY rownum DESC")

    cur.execute(statement % (sender_id, receiver_id, receiver_id, sender_id))
    messages = cur.fetchall()

    cur.close()
    connection.close()

    dict = {
        'username': request.session['username'],
        'user_id': request.session['user_id'],
        'receiver_id': receiver_id,
        'receiver_name': receiver_name,
        'messages': messages
    }

    return render(request, 'chat_box_inner.html', dict)


