
import os

if __name__ == '__main__':
    # 加载Django项目的配置信息
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booksys.settings")
    # 导入Django，并启动Django项目
    import django
    django.setup()

    from books import models
    # 查询所有的人
    # ret = models.Author.objects.all()
    # print(ret)
    # # get查询
    # ret = models.Author.objects.get(name="钟瑞琪")
    # print(ret)
    # # filter
    # ret = models.Author.objects.filter(id=100)  # 不存在返回一个空的QuerySet，不会报错
    # print(ret)
    # # 就算查询的结果只有一个，返回的也是QuerySet，我们要用索引的方式取出第一个元素
    # ret = models.Author.objects.filter(id=1)
    # print(ret)
    # print("exclude".center(80, "*"))
    # # exclude
    # ret = models.Author.objects.exclude(id=1)
    # print(ret)
    # print("values".center(80, "*"))
    # # values 返回一个QuerySet对象，里面都是字典。 不写字段名，默认查询所有字段
    # ret = models.Author.objects.values("name")
    # print(ret)
    # print("values_list".center(80, "*"))
    # # values_list 返回一个QuerySet对象，里面都是元祖。 不写字段名，默认查询所有字段
    # ret = models.Author.objects.values_list()
    # print(ret)
    # print("order_by".center(80, "*"))
    # # order_by 按照指定的字段排序
    # ret = models.Author.objects.all().order_by("name")
    # print(ret)
    # print("reverse".center(80, "*"))
    # # reverse 将一个有序的QuerySet 反转顺序
    # # 对有序的QuerySet才能调用reverse
    # ret = models.Author.objects.all().reverse()
    # print(ret)
    # print("count".center(80, "*"))
    # # count 返回QuerySet中对象的数量
    # ret = models.Author.objects.all().count()
    # print(ret)
    # print("first".center(80, "*"))
    # # first 返回QuerySet中第一个对象
    # ret = models.Author.objects.all().first()
    # print(ret)
    # print("last".center(80, "*"))
    # # last 返回QuerySet中最后一个对象
    # ret = models.Author.objects.all().last()
    # print(ret)
    # print("exists".center(80, "*"))
    # # exists 判断表里有没有数据
    # ret = models.Book.objects.exists()
    # print(ret)

    ret = models.Book.objects.first().publisher.name
    print(ret)
    ret = models.Book.objects.values_list('publisher__name')
    print(ret)
    ret = models.Publisher.objects.first().book_set.all()
    print(ret)
    ret = models.Publisher.objects.values_list('book__title')
    print(ret)
    ret = models.Author.objects.values("name")
    print(ret)