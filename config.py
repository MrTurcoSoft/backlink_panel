# config.py
import os
import secrets

#print(secrets.token_hex(32))
class Config:
    SECRET_KEY = 'c61c30dd38801ec0dd1de66248171432689dd1f8c8abc08e7924a9df2c543843'
    # MySQL veritabanı bağlantı bilgileri
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:Asli281019*Cagdas@db:3306/backlink?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    MIN_PAGE_RANK = 3
