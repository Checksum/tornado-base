import os
import datetime

from peewee import *

db = SqliteDatabase('database.db', threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    email = CharField(unique=True, null=False)
    name = CharField(null=False)
    password = CharField(null=False)
