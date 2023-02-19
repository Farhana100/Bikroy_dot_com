from django.db import models


class USER(models.Model):
    def __init__(self, NAME, LOCATION, SUB_LOCATION, POST_COUNT):
        self.NAME = NAME
        self.LOCATION = LOCATION
        self.SUB_LOCATION = SUB_LOCATION
        self.POST_COUNT = POST_COUNT


class PRODUCT_AD(models.Model):

    def __init__(self, PRODUCT_AD_ID, TITLE, DESCRIPTION, TIME_OF_POST, PRICE, NEGOTIABLE, CONDITION, CATEGORY, SUB_CATEGORY,Image,phone):
        self.PRODUCT_AD_ID = PRODUCT_AD_ID
        self.TITLE = TITLE
        self.DESCRIPTION = DESCRIPTION
        self.TIME_OF_POST = TIME_OF_POST
        self.PRICE = PRICE
        self.NEGOTIABLE = NEGOTIABLE
        self.CONDITION = CONDITION
        self.CATEGORY = CATEGORY
        self.SUB_CATEGORY = SUB_CATEGORY
        self.Image = Image
        self.phone = phone


class PROD_AD_TYPE(models.Model):
    def __init__(self,AD_TYPE_ID, AD_TYPE):
        self.AD_TYPE_ID = AD_TYPE_ID
        self.AD_TYPE = AD_TYPE


class REPORT(models.Model):
    def __init__(self,reason,email,message,reported_ad_id):
        self.reason = reason
        self.email = email
        self.message = message
        self.reported_ad_id = reported_ad_id


class MEMBER(models.Model):
    def __init__(self,id,type,date,duration,payment_status):
        self.id = id
        self.type = type
        self.date = date
        self.duration = duration
        self.payment_status = payment_status

