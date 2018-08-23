import time
from pymongo import MongoClient

monmod = MongoClient()


def timestamp():
    return int(time.time())


def next_id(name):
    query = {
        'name': name,
    }
    update = {
        '$inc': {
            'seq': 1
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    # 存储数据的 id
    doc = monmod.db['data_id']
    new_id = doc.find_and_modify(**kwargs).get('seq')
    return new_id


class Monmod(object):
    __fields__ = [
        '_id',  # 给数据库里面的 _id 留一个位置
        # (字段名, 类型, 值)
        ('id', int, -1),
        ('type', str, ''),
        ('type', str, ''),
        ('deleted', bool, False),
        ('created_time', int, 0),
        ('updated_time', int, 0),
    ]

    @classmethod
    def has(cls, **kwargs):
        """
        检查一个元素是否在数据库中 用法如下
        User.hsa(id=1)
        :param kwargs:
        :return:
        """
        return cls.find_one(**kwargs) is not None

    def mongos(self, name):
        return monmod.db[name]._find()

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())

        return '<{0}: \n  {1}\n>'.format(classname, '\n  '.join(properties))

    @classmethod
    def new(cls, form=None, **kwargs):
        """
        new 是给外部使用的函数
        :param form:
        :param kwargs:
        :return:
        """
        name = cls.__name__
        # 创建一个空对象
        m = cls()
        # 把定义的数据写入空对象，未定义的数据输出错误
        fields = cls.__fields__.copy()
        # 去掉 _id 这个特殊字段
        fields.remove('_id')
        if form is None:
            form = {}

        for f in fields:
            k, t, v = f
            if k in form:
                setattr(m, k, t(form[k]))
            else:
                # 设置默认值
                setattr(m, k, v)

        # 处理额外的参数
        for k, v in kwargs.items():
            if hasattr(m, k):
                setattr(m, k, v)
            else:
                raise KeyError

        # 写入默认数据
        m.id = next_id(name)
        ts = int(timestamp())
        m.created_time = m.updated_time = ts
        m.type = name.lower()
        m.save()
        return m

    @classmethod
    def _new_with_bson(cls, bson):
        """
        这是给内部 all 这种函数使用的函数
        从 mongo 数据中恢复一个 model
        :param cls:
        :param bson:
        :return:
        """
        m = cls()
        fields = cls.__fields__.copy()
        # 去掉 _id 这个特殊字段
        fields.remove('_id')
        for f in fields:
            k, t, v = f
            if k in bson:
                setattr(m, k, bson[k])
            else:
                # 设置默认值
                setattr(m, k, v)
        setattr(m, '_id', bson['_id'])
        # 这一句必不可少, 否则 bson 生成 一个新的 _id
        # FIXME, 因为现在的数据库里面未必有 type
        # 所以在这里强行加上
        # 以后洗掉 db 的数据后应该删掉这一句
        m.type = cls.__name__.lower()
        return m

    @classmethod
    def all(cls):
        return cls._find()

    # TODO, 应该还有一个函数 find(name, **kwargs)
    @classmethod
    def _find(cls, **kwargs):
        """
        mongo 数据查询
        :param kwargs:
        :return:
        """
        name = cls.__name__
        # TODO 过滤删除的元素
        flag_sort = '__sort'
        sort = kwargs.pop(flag_sort, None)
        ds = monmod.db[name].find(kwargs)
        if sort is not None:
            ds = ds.sort(sort)
        l = [cls._new_with_bson(d) for d in ds]
        return l

    @classmethod
    def _find_raw(cls, **kwargs):
        name = cls.__name__
        ds = monmod.db[name]._find(kwargs)
        return list(ds)

    @classmethod
    def find_all(cls, **kwargs):
        name = cls.__name__
        ds = monmod.db[name].find(**kwargs)
        if ds is None:
            return None
        return list(ds)

    @classmethod
    def _clean_field(cls, source, target):
        """
        清洗数据用的函数
        例如 User._clean_field('is_hidden', 'deleted)
        把 is_hidden 字段全部复制为 deleted 字段
        """
        ms = cls._find()
        for m in ms:
            v = getattr(m, source)
            setattr(m, target, v)
            m.save()

    @classmethod
    def find_by(cls, **kwargs):
        return cls.find_one(**kwargs)

    @classmethod
    def find(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def get(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def find_one(cls, **kwargs):
        # TODO 过滤掉被删除的元素
        l = cls._find(**kwargs)
        if len(l) > 0:
            return l[0]
        else:
            return None

    @classmethod
    def upsert(cls, query_form, update_form, hard=False):
        ms = cls.find_one(**query_form)
        if ms is None:
            query_form.update(**update_form)
            ms = cls.new(query_form)
        else:
            ms.update(update_form, hard=hard)
        return ms

    def update(self, form, hard=False):
        for k, v in form.items():
            if hard or hasattr(self, k):
                setattr(self, k, v)
        self.save()

    def save(self):
        name = self.__class__.__name__
        # save 函数 如果你有 _id 相当于 update
        # 如果没有 相当于 insert
        monmod.db[name].save(self.__dict__)

    def delete(self):
        name = self.__class__.__name__
        query = {
            'id': self.id,
        }
        values = {
            'deleted': True,
        }
        monmod.db[name].update_one(query, values)

    def blacklist(self):
        b = [
            '_id',
        ]
        return b

    def json(self):
        _dict = self.__dict__
        d = {k: v for k, v in _dict.items() if k not in self.blacklist()}
        # TODO, 增加一个 type 属性
        return d

    def data_count(self, cls):
        """
        神奇的函数，查看用户发表的评论数
        u.date_count(Comment
        """
        name = cls.__name__
        # TODO 这里应该用 tyoe 替代
        fk = '{}_id'.format(self.__class__.__name__.lower())
        query = {
            fk: self.id,
        }
        count = monmod.db[name]._find(query).count()
        return count
