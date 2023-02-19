from django.shortcuts import render
from django.shortcuts import redirect
import cx_Oracle
from django.contrib.auth.hashers import make_password, check_password

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='orcl')


# Create your views here.

def home(request):
    city_loc = []
    div_loc = []
    city_sub_loc = {}
    div_sub_loc = {}

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT LOCATION_ID, LOCATION_NAME FROM  LOCATIONS WHERE PARENT_ID IS NULL"
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
    dict = {'city_loc': city_loc,
            'div_loc': div_loc,
            'city_sub_loc': city_sub_loc,
            'div_sub_loc': div_sub_loc}

    statement = "SELECT CATEGORY_NAME,CAT_DESCRIPTION,IMAGE_CAT FROM CATEGORIES WHERE PARENT_ID IS NULL"
    cur.execute(statement)

    categories_all = cur.fetchall()

    first = cur.var(str)
    second = cur.var(str)
    third = cur.var(str)

    statement = "BEGIN TOP_THREE_CAT(:1,:2, :3); END;"
    cur.execute(statement, [first, second, third])

    statement = """SELECT IMAGE_CAT FROM CATEGORIES 
                    WHERE CATEGORY_NAME = '%s'"""

    cur.execute(statement % first.getvalue())
    first_img, = cur.fetchall()[0]

    cur.execute(statement % second.getvalue())
    second_img, = cur.fetchall()[0]

    cur.execute(statement % third.getvalue())
    third_img, = cur.fetchall()[0]

    cur.close()
    connection.close()

    dict['categories_all'] = categories_all
    dict['first'] = first.getvalue()
    dict['second'] = second.getvalue()
    dict['third'] = third.getvalue()
    dict['first_img'] = first_img
    dict['second_img'] = second_img
    dict['third_img'] = third_img

    if request.session.has_key('username'):
        dict['username'] = request.session['username']
        return render(request, 'index.html', dict)
    else:
        dict['username'] = ''
        return render(request, 'index.html', dict)


def register_form(request):
    return render(request, 'register.html')


def register(request):
    name = str(request.POST['name'])
    email = str(request.POST['email'])
    password = str(request.POST['password'])
    password_confirm = str(request.POST['password_confirm'])

    statement = "SELECT NAME FROM USER_ WHERE EMAIL_ADDR = '%s'"
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement % email)
    result = cur.fetchall()

    cur.close()
    connection.close()

    if result:
        return render(request, 'register.html', {'message': "E-mail ID already registered"})
    elif password != password_confirm:
        return render(request, 'register.html', {'message': "passwords don't match"})

    # now inserting new user info

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT MAX(USER_ID) FROM USER_"
    cur.execute(statement)

    new_id, = cur.fetchall()[0]

    if new_id is None:
        new_id = 0
    new_id += 1

    password = make_password(password)

    statement = "INSERT INTO USER_ (USER_ID, NAME, PASSWORD, EMAIL_ADDR, LAST_UPDATE_TIME, POST_COUNT) VALUES ( %s, '%s', '%s', '%s',SYSDATE, 0)"
    cur.execute(statement % (new_id, name, password, email))
    cur.close()

    connection.commit()
    connection.close()

    request.session['username'] = name
    request.session['email'] = email
    request.session['user_id'] = new_id
    return redirect('home')


def login(request, message=None):
    if request.session.has_key('username'):
        return redirect('home')
    return render(request, 'log_in_page.html', message)


def verify_pass(request):
    name = None
    email = str(request.POST['email'])
    password = str(request.POST['password'])

    statement = "SELECT PASSWORD FROM USER_ WHERE EMAIL_ADDR = '%s'"
    statement2 = "SELECT USER_ID, NAME FROM USER_ WHERE EMAIL_ADDR = '%s'"
    hashed_pass = None

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement % email)
    result = cur.fetchall()

    user_id = None

    if result:
        hashed_pass, = result[0]

        cur.execute(statement2 % email)
        name = cur.fetchall()
        user_id, name, = name[0]
    else:
        hashed_pass = ''

    cur.close()
    connection.close()

    if check_password(password, hashed_pass):
        request.session['username'] = name
        request.session['email'] = email
        request.session['user_id'] = user_id
        return redirect('home')
    else:
        message = 'incorrect E-mail Id or Password'
        return login(request, {'message': message})


def signout(request):
    # delete session here
    request.session.flush()
    request.session.clear_expired()

    return redirect('home')


def search_ads(request):
    filt = request.session['filter']
    del (request.session['filter'])
    normal_ads = []
    top_ads = []
    spot_ads = []
    urg_ads = []

    if filt == "all":
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()

        statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                     "WHERE PRODUCT_AD_ID = PROD_IMAGE_ID "
                     "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                     "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                     "AND (AD_TYPE LIKE 'normal' OR AD_TYPE LIKE '%update%') "
                     "AND APPROVER_ID IS NOT NULL"
                     " ORDER BY TIME_OF_POST DESC")
        cur.execute(statement)
        normal_ads = cur.fetchall()

        statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                     "WHERE PRODUCT_AD_ID = PROD_IMAGE_ID "
                     "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                     "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                     "AND AD_TYPE LIKE '%s' "
                     "AND APPROVER_ID IS NOT NULL"
                     " ORDER BY TIME_OF_POST DESC")
        cur.execute(statement % 'top')
        top_ads = cur.fetchall()

        cur.execute(statement % 'spot')
        spot_ads = cur.fetchall()

        cur.execute(statement % 'urg')
        urg_ads = cur.fetchall()

        cur.close()
        connection.close()
    else:
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                     "WHERE (LOWER(PRODUCT_AD.TITLE) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.DESCRIPTION) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.CATEGORY) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.SUB_CATEGORY) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.LOCATION) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.SUB_LOCATION) LIKE LOWER('%s') "
                     ") "
                     "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                     "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                     "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                     "AND (AD_TYPE LIKE 'normal' OR AD_TYPE LIKE '%s') "
                     "AND APPROVER_ID IS NOT NULL "
                     " ORDER BY TIME_OF_POST DESC"
                     )
        cur.execute(statement % (filt, filt, filt, filt, filt, filt, '%update%'))
        normal_ads = cur.fetchall()

        statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                     "WHERE (LOWER(PRODUCT_AD.TITLE) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.DESCRIPTION) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.CATEGORY) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.SUB_CATEGORY) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.LOCATION) LIKE LOWER('%s') "
                     "OR LOWER(PRODUCT_AD.SUB_LOCATION) LIKE LOWER('%s') "
                     ") "
                     "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                     "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                     "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                     "AND AD_TYPE LIKE '%s' "
                     "AND APPROVER_ID IS NOT NULL "
                     " ORDER BY TIME_OF_POST DESC"
                     )
        cur.execute(statement % (filt, filt, filt, filt, filt, filt, 'top'))
        top_ads = cur.fetchall()

        cur.execute(statement % (filt, filt, filt, filt, filt, filt, 'spot'))
        spot_ads = cur.fetchall()

        cur.execute(statement % (filt, filt, filt, filt, filt, filt, 'urg'))
        urg_ads = cur.fetchall()

        cur.close()
        connection.close()

    ads = {
        'normal_ads': normal_ads,
        'top_ads': top_ads,
        'spot_ads': spot_ads,
        'urg_ads': urg_ads,
    }

    return ads


def all_ads(request):
    if request.GET.get('filter'):
        filt = "%" + request.GET['filter'] + "%"
        request.session['filter'] = filt

    if not request.session.has_key('filter'):
        request.session['filter'] = 'all'

    ads = search_ads(request)

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

    cur.close()
    connection.close()

    dict = {
        'city_loc': city_loc,
        'div_loc': div_loc,
        'city_sub_loc': city_sub_loc,
        'div_sub_loc': div_sub_loc,
        'cat': cat,
        'sub_cat': sub_cat,
        'normal_ads': ads['normal_ads'],
        'top_ads': ads['top_ads'],
        'spot_ads': ads['spot_ads'],
        'urg_ads': ads['urg_ads'],
    }
    if request.session.has_key('username'):
        dict['username'] = request.session['username']
        return render(request, 'all_ads_page.html', dict)
    else:
        dict['username'] = ''
        return render(request, 'all_ads_page.html', dict)


def get_ad(request):
    post_id = int(request.POST['view_post_id'])

    request.session['post_id'] = post_id
    return redirect('view_ad')


def view_ad(request):
    message = ""
    if request.session.has_key('report_message'):
        message = request.session['report_message']
        del (request.session['report_message'])

    post_id = int(request.session['post_id'])

    connection = cx_Oracle.connect(user="PROJECT_BIKROY", password="Oblivious", dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = %s "
                 "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID")
    cur.execute(statement % str(post_id))

    post_id, title, description, time, price, is_nego, condition, category, subcategory, location, sublocation, _, poster_id, _, image_name, _, ad_type, _, contact_num = \
        cur.fetchall()[0]

    statement = "SELECT NAME FROM USER_ WHERE USER_ID = %s"
    cur.execute(statement % str(poster_id))
    poster_name, = cur.fetchall()[0]

    temp_id = -1
    if request.session.has_key('user_id'):
        temp_id = request.session['user_id']

    statement = "SELECT * FROM FAVOURITE WHERE FAV_AD_ID = %s AND FAV_USER_ID = %s"
    cur.execute(statement % (post_id, temp_id))
    is_fav = cur.fetchall()

    cur.close()
    connection.close()

    desc_len = len(description)

    dict = {'post_id': post_id, 'title': title, 'description': description, 'time': time, 'price': price,
            'is_nego': is_nego, 'condition': condition, 'category': category, 'subcategory': subcategory,
            'location': location, 'sublocation': sublocation, 'poster_id': poster_id, 'image_name': image_name,
            'contact_num': contact_num, 'user_id': None, 'message': message, 'ad_type': ad_type,
            'email': None, 'poster_name': poster_name, 'desc_len': desc_len, 'is_fav': is_fav}

    if request.session.has_key('username'):
        dict['username'] = request.session['username']
        dict['user_id'] = request.session['user_id']
        dict['email'] = request.session['email']

    return render(request, 'view_ad_page.html', dict)


def reporting_ad(request):
    reason = request.POST['reason']
    reporter_email = request.POST['reporter_email']
    reporter_message = request.POST['reporter_message']
    reported_post_id = request.POST['reported_post_id']

    connection = cx_Oracle.connect(user="PROJECT_BIKROY", password="Oblivious", dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT MAX(REPORT_ID) FROM REPORT"

    cur.execute(statement)

    report_id, = cur.fetchall()[0]
    if report_id is None:
        report_id = 0
    report_id += 1

    statement = ("INSERT INTO REPORT(REPORT_ID, REASON, EMAIL_ADDR, REPORT_MESSAGE, REPORTED_AD_ID) "
                 "VALUES(%s, '%s', '%s', '%s', %s)")

    cur.execute(statement % (report_id, reason, reporter_email, reporter_message, reported_post_id))

    cur.close()
    connection.commit()
    connection.close()

    request.session['report_message'] = 'Ad reported to admin'
    return redirect('view_ad')


def delete_post(request):
    post_id = request.POST["delete_post"]
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = "DELETE FROM PRODUCT_AD WHERE PRODUCT_AD_ID= '%s'"
    cur.execute(statement % post_id)

    connection.commit()
    cur.close()
    connection.close()
    return redirect('my_account_page')
