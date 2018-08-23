import pymongo
import random


client = pymongo.MongoClient("mongodb://localhost:27017")
print("连接数据库成功", client)

mongdb_name = "demo"
db = client[mongdb_name]


def insert():
    u = {
        'name': 'ts',
        'note': 'zjt',
        '随机值': random.randint(0, 3)
    }
    db.user.insert_one(u)
# 相当于

def find():
    user_list = list(db.user.find())
    print('所有用户', user_list)


def find_condition1():
    query = {
        '随机值': 1
    }
    us = list(db.user.find(query))
    print('us', us)


def find_condition1():
    query = {
        '随机值': {
            '$gt': 1
        },
    }
    # 查询 随机值 大于 1  