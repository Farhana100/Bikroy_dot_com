from django.shortcuts import render
from django.shortcuts import redirect
import cx_Oracle
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import default_storage
from datetime import date

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='orcl')


def AdminPage(request):
    if not request.session.has_key('admin_username'):
        return redirect('admin_login')

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID "
                 "AND APPROVER_ID IS NULL")

    cur.execute(statement)
    AdList = cur.fetchall()

    statement = "SELECT * FROM REPORT "
    cur.execute(statement)
    reports = cur.fetchall()

    cur.close()
    connection.close()

    dict = {'AdList': AdList, 'reports': reports}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'Admin_page.html', dict)


def admin_login(request, message=None):
    if request.session.has_key('admin_username'):
        return redirect('AdminPage')
    return render(request, 'Admin_login_page.html', message)


def check_admin(request):
    if request.session.has_key('admin_username'):
        return redirect('AdminPage')
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    email = str(request.POST['email'])
    password = str(request.POST['password'])

    statement = ("SELECT USER_.PASSWORD, ADMIN.DESIGNATION "
                 "FROM ADMIN, USER_ "
                 "WHERE USER_.EMAIL_ADDR = '%s' "
                 "AND ADMIN.ADMIN_ID = USER_.USER_ID ")

    statement2 = "SELECT USER_ID, NAME FROM USER_ WHERE EMAIL_ADDR = '%s'"
    hashed_pass = None
    admin_user_id = None
    admin_username = None
    cur.execute(statement % email)
    result = cur.fetchall()

    des = None

    if result:
        hashed_pass, des, = result[0]

        cur.execute(statement2 % email)
        name = cur.fetchall()[0]
        admin_user_id = int(name[0])
        admin_username = str(name[1])
        cur.close()
        connection.close()

    else:
        hashed_pass = ''

    print(des)

    if check_password(password, hashed_pass):
        request.session['admin_user_id'] = admin_user_id
        request.session['admin_username'] = admin_username
        request.session['user_id'] = admin_user_id
        request.session['username'] = admin_username
        request.session['email'] = email

        if str(des) == 'Manager':
            print("manager")
            request.session['manager'] = 'manager'
        return redirect('AdminPage')

    message = "incorrect E-mail Id or Password\nN.B if you are not an Admin, you are not allowed to log in"
    return admin_login(request, {'message': message})


def show_ad(request):
    post_id = int(request.POST['view_post_id'])

    request.session['post_id'] = post_id
    return redirect('admin_view_ad')


def admin_view_ad(request):
    post_id = int(request.session['post_id'])

    connection = cx_Oracle.connect(user="PROJECT_BIKROY", password="Oblivious", dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = %s "
                 "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID")

    cur.execute(statement % str(post_id))

    post_id, title, description, time, price, is_nego, condition, category, subcategory, location, sublocation, _, poster_id, _, image_name, _, _, _, contact_num = \
        cur.fetchall()[0]

    statement = "SELECT NAME FROM USER_ WHERE USER_ID = %s"
    cur.execute(statement % str(poster_id))
    poster_name, = cur.fetchall()[0]

    cur.close()
    connection.close()

    desc_len = len(description)

    dict = {'post_id': post_id, 'title': title, 'description': description, 'time': time, 'price': price,
            'is_nego': is_nego, 'condition': condition, 'category': category, 'subcategory': subcategory,
            'location': location, 'sublocation': sublocation, 'poster_id': poster_id, 'image_name': image_name,
            'contact_num': contact_num, 'admin_user_id': request.session['admin_user_id'],
            'admin_username': request.session['admin_username'],
            'email': request.session['email'], 'poster_name': poster_name, 'desc_len': desc_len}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'show_ad_page.html', dict)


def approve_ad(request):
    if 'Approved_prod_id' in request.POST:
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        Approved_prod_id = str(request.POST['Approved_prod_id'])
        approver_id = str(request.session['admin_user_id'])
        statement = "UPDATE PRODUCT_AD SET APPROVER_ID = %s WHERE PRODUCT_AD_ID = %s"
        cur.execute(statement % (approver_id, Approved_prod_id))
        connection.commit()
        cur.close()
        connection.close()
    return redirect('AdminPage')


def discard_ad(request):
    if 'discarded_ad_id' in request.POST:
        if request.session.has_key('post_id'):
            del (request.session['post_id'])
        discarded_ad_id = str(request.POST['discarded_ad_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "DELETE FROM PRODUCT_AD WHERE PRODUCT_AD_ID = '%s'"
        cur.execute(statement % discarded_ad_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('AdminPage')


def show_report(request):
    reported_id = int(request.POST['reported_id'])

    request.session['reported_id'] = reported_id
    return redirect('open_report')


def open_report(request):
    reported_id = str(request.session['reported_id'])

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = %s "
                 "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID ")

    cur.execute(statement % reported_id)
    reported_ad = cur.fetchall()[0]

    post_id, title, description, time, price, is_nego, condition, category, subcategory, location, sublocation, _, poster_id, _, image_name, _, _, _, contact_num = reported_ad

    statement = "SELECT  * FROM REPORT WHERE REPORTED_AD_ID = '%s'"
    cur.execute(statement % reported_id)
    reports = cur.fetchall()

    statement = "SELECT NAME, EMAIL_ADDR FROM USER_ WHERE USER_ID = %s"
    cur.execute(statement % str(poster_id))
    poster_name, poster_email = cur.fetchall()[0]

    cur.close()
    connection.close()

    desc_len = len(description)

    dict = {'post_id': post_id, 'title': title, 'description': description, 'time': time, 'price': price,
            'is_nego': is_nego, 'condition': condition, 'category': category, 'subcategory': subcategory,
            'location': location, 'sublocation': sublocation, 'poster_id': poster_id, 'image_name': image_name,
            'contact_num': contact_num, 'admin_user_id': request.session['admin_user_id'],
            'admin_username': request.session['admin_username'], 'email': request.session['email'],
            'poster_name': poster_name, 'poster_email': poster_email, 'desc_len': desc_len, 'reports': reports}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'show_report.html', dict)


def discard_report(request):
    if 'Ignored_ad_id' in request.POST:
        if request.session.has_key('reported_id'):
            del (request.session['reported_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()

        Ignored_ad_id = str(request.POST['Ignored_ad_id'])
        statement = "DELETE FROM REPORT WHERE REPORTED_AD_ID = '%s'"
        cur.execute(statement % Ignored_ad_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('AdminPage')


def discard_report_ad(request):
    if 'discarded_ad_id' in request.POST:
        if request.session.has_key('reported_id'):
            del (request.session['reported_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()

        discarded_ad_id = str(request.POST['discarded_ad_id'])
        statement = "DELETE FROM PRODUCT_AD WHERE PRODUCT_AD_ID = '%s'"
        cur.execute(statement % discarded_ad_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('AdminPage')


def remove_post_ad(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID")

    cur.execute(statement)
    AdList = cur.fetchall()

    dict = {'AdList': AdList}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'
    return render(request, 'remove_post_ad.html', dict)


def remove_ad(request):
    if 'discarded_ad_id' in request.POST:
        discarded_ad_id = str(request.POST['discarded_ad_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()

        statement = "DELETE FROM PRODUCT_AD WHERE PRODUCT_AD_ID = '%s'"
        cur.execute(statement % discarded_ad_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('remove_post_ad')


def update_post_type(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = ("SELECT * FROM PRODUCT_AD, PROD_IMAGE, PROD_AD_TYPE, PROD_PHONE_NUM "
                 "WHERE LOWER(PROD_AD_TYPE.AD_TYPE) LIKE '%update%' "
                 "AND PRODUCT_AD_ID = PROD_IMAGE_ID "
                 "AND PRODUCT_AD_ID = PROD_TYPE_ID "
                 "AND PRODUCT_AD_ID = PROD_PHONE_ID")
    cur.execute(statement)
    list = cur.fetchall()
    cur.close()
    connection.close()

    dict = {'list': list}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'update_post_type.html', dict)


def Promote_ad(request):
    if 'promote_ad_id' in request.POST:
        promote_ad_id = str(request.POST['promote_ad_id'])
        types = str(request.POST['types'])
        typelist = types.split('-')
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "DELETE FROM PROD_AD_TYPE WHERE PROD_TYPE_ID = '%s'"
        cur.execute(statement % promote_ad_id)
        for type in typelist:
            if type == 'update':
                continue
            statement = "INSERT INTO PROD_AD_TYPE VALUES('%s','%s')"
            cur.execute(statement % (promote_ad_id, str(type)))
        connection.commit()
        cur.close()
        connection.close()
    return redirect('update_post_type')


def discard_promote_request(request):
    if 'discarded_type_id' in request.POST:
        discarded_type_id = str(request.POST['discarded_type_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "UPDATE PROD_AD_TYPE SET AD_TYPE = 'normal' WHERE PROD_TYPE_ID = '%s'"
        cur.execute(statement % discarded_type_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('update_post_type')


def make_member(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = ("SELECT U.USER_ID, U.NAME, U.EMAIL_ADDR, M.MEMBERSHIP_TYPE, M.MEMBERSHIP_DATE, ADD_MONTHS("
                 "M.MEMBERSHIP_DATE, M.DURATION) EXP_DATE, TRUNC(ADD_MONTHS(M.MEMBERSHIP_DATE, M.DURATION) - SYSDATE, 0) TIME_LEFT "
                 "FROM MEMBER M, USER_ U "
                 "WHERE PAYMENT_SATUS = 'N' "
                 "AND MEMBER_ID = USER_ID")
    cur.execute(statement)
    member_req_list = cur.fetchall()

    dict = {'member_req_list': member_req_list}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'make_member.html', dict)


def approve_membership(request):
    if 'Approved_id' in request.POST:
        Approved_id = str(request.POST['Approved_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "UPDATE MEMBER SET PAYMENT_SATUS = 'Y' WHERE MEMBER_ID = %s"
        cur.execute(statement % Approved_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('make_member')


def discard_membership(request):
    if 'discarded_id' in request.POST:
        discarded_id = str(request.POST['discarded_id'])
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "DELETE FROM MEMBER WHERE MEMBER_ID = %s"
        cur.execute(statement % discarded_id)
        connection.commit()
        cur.close()
        connection.close()
    return redirect('make_member')


def add_loc_cat(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement1 = "SELECT LOCATION_NAME FROM LOCATIONS WHERE PARENT_ID IS NULL"
    statement2 = "SELECT CATEGORY_NAME FROM CATEGORIES WHERE PARENT_ID IS NULL"
    cur.execute(statement1)
    result = cur.fetchall()

    locations = []
    for loc in result:
        locations.append(loc[0])

    categories = []
    cur.execute(statement2)
    result = cur.fetchall()

    for cat in result:
        categories.append(cat[0])

    dict = {'locations': locations, 'categories': categories}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'
    return render(request, 'new_loc_cat.html', dict)


def add_new_loc(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT COUNT(*) FROM LOCATIONS"
    cur.execute(statement)
    new_id, = cur.fetchall()[0]

    new_id += 1
    new_loc = str(request.POST['new_loc'])
    statement = "INSERT INTO LOCATIONS(LOCATION_ID,LOCATION_NAME) VALUES ( '%s','%s')"
    cur.execute(statement % (str(new_id), new_loc))
    connection.commit()
    cur.close()
    connection.close()
    return redirect('add_loc_cat')


def add_new_subloc(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    loc = request.POST['add_to_loc']
    new_sub_loc = str(request.POST['new_sub_loc'])

    statement = "SELECT LOCATION_ID FROM LOCATIONS WHERE LOCATION_NAME = '%s'"
    cur.execute(statement % str(loc))
    parent_id, = cur.fetchall()[0]

    statement = "SELECT COUNT(*) FROM LOCATIONS"
    cur.execute(statement)
    new_id, = cur.fetchall()[0]

    new_id += 1
    statement = "INSERT INTO LOCATIONS VALUES( '%s','%s','%s')"
    cur.execute(statement % (str(new_id), new_sub_loc, str(parent_id)))
    connection.commit()
    cur.close()
    connection.close()
    return redirect('add_loc_cat')


def add_new_cat(request):
    new_cat_description = str(request.POST['new_cat_description'])
    new_cat = str(request.POST['new_cat'])
    img1 = request.FILES['img1']

    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = "SELECT COUNT(*) FROM CATEGORIES"
    cur.execute(statement)
    new_id, = cur.fetchall()[0]

    new_id += 1
    img1_name = str(new_id) + "_" + str(new_cat) + "." + img1.name.split(".")[-1];

    statement = "INSERT INTO CATEGORIES(CATEGORY_ID,CATEGORY_NAME,CAT_DESCRIPTION,IMAGE_CAT) VALUES('%s','%s','%s','%s')"
    cur.execute(statement % (str(new_id), new_cat, new_cat_description, img1_name))
    connection.commit()
    cur.close()
    connection.close()

    default_storage.save(img1_name, img1)
    return redirect('add_loc_cat')


def add_new_subcat(request):
    cat = str(request.POST['add_to_cat'])
    new_sub_cat = str(request.POST['new_sub_cat'])
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = "SELECT CATEGORY_ID FROM CATEGORIES WHERE CATEGORY_NAME = '%s'"
    cur.execute(statement % str(cat))
    parent_id, = cur.fetchall()[0]

    statement = "SELECT COUNT(*) FROM CATEGORIES"
    cur.execute(statement)
    new_id, = cur.fetchall()[0]

    new_id += 1
    statement = "INSERT INTO CATEGORIES(CATEGORY_ID,CATEGORY_NAME,PARENT_ID) VALUES ('%s','%s','%s')"
    cur.execute(statement % (str(new_id), new_sub_cat, str(parent_id)))
    connection.commit()
    cur.close()
    connection.close()
    return redirect('add_loc_cat')


def delete_expired_ads(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = "SELECT PAYMENT_SATUS FROM MEMBER WHERE MEMBER_ID = %s"
    cur.execute(statement % request.session['user_id'])
    is_member = cur.fetchall()
    if not is_member or is_member[0][0] == 'N':
        statement = "DELETE FROM PRODUCT_AD WHERE (SYSDATE-TIME_OF_POST)>=3"
        cur.execute(statement)
        connection.commit()
    cur.close()
    connection.close()
    return redirect('remove_post_ad')


def all_members(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    statement = ("SELECT U.USER_ID, U.NAME, U.EMAIL_ADDR, M.MEMBERSHIP_TYPE, M.MEMBERSHIP_DATE, ADD_MONTHS("
                 "M.MEMBERSHIP_DATE, M.DURATION) EXP_DATE, TRUNC(ADD_MONTHS(M.MEMBERSHIP_DATE, M.DURATION) - SYSDATE, 0) TIME_LEFT "
                 "FROM MEMBER M, USER_ U "
                 "WHERE PAYMENT_SATUS = 'Y' "
                 "AND MEMBER_ID = USER_ID")
    cur.execute(statement)
    member_list = cur.fetchall()
    cur.close()
    connection.close()

    dict = {'member_list': member_list}

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'all_members.html', dict)


def delete_all_expired_members(request):
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()
    statement = "DELETE FROM MEMBER WHERE (ADD_MONTHS(MEMBERSHIP_DATE,DURATION))<SYSDATE"
    cur.execute(statement)
    connection.commit()
    cur.close()
    connection.close()
    return redirect('all_members')


def make_admin(request):
    dict = {}
    if request.session.has_key('make_admin_msg'):
        dict['make_admin_msg'] = request.sesion['make_admin_msg']
        del(request.session['make_admin_msg'])

    if request.session.has_key('manager'):
        dict['manager'] = 'manager'

    return render(request, 'make_admin.html', dict)


def register_admin(request):
    name = str(request.POST['name'])
    des = str(request.POST['des'])
    email = str(request.POST['email'])
    password = str(request.POST['password'])
    password_confirm = str(request.POST['password_confirm'])

    statement = "SELECT USER_ID FROM USER_ WHERE EMAIL_ADDR = '%s'"
    connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
    cur = connection.cursor()

    cur.execute(statement % email)
    result = cur.fetchall()

    cur.close()
    connection.close()

    if result:
        u_id, = result[0]
        connection = cx_Oracle.connect(user='PROJECT_BIKROY', password='Oblivious', dsn=dsn_tns)
        cur = connection.cursor()
        statement = "INSERT INTO ADMIN VALUES(%s, '%s')"
        cur.execute(statement % (u_id, des))

        cur.close()
        connection.commit()
        connection.close()

        request.session['make_admin_msg'] = name + " is now an Admin."
        return redirect('make_admin')
    elif password != password_confirm:
        dict = {'message': "passwords don't match"}
        if request.session.has_key('manager'):
            dict['manager'] = 'manager'

        return render(request, 'make_admin.html', dict)

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

    statement = "INSERT INTO ADMIN VALUES(%s, '%s')"
    cur.execute(statement % (new_id, des))

    cur.close()

    connection.commit()
    connection.close()

    request.session['make_admin_msg'] = name + " is now an Admin"
    return redirect('make_admin')
