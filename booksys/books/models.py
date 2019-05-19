from django.db import models

# Create your models here.
# 图书管理系统

#出版社
class Publisher(models.Model):
    id = models.AutoField(primary_key=True) # 自增的ID主键
    name = models.CharField(max_length=64,null=False,unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return "<Publisher Object:{}".format(self.name)

#书
class Book(models.Model):
    id = models.AutoField(primary_key=True)# 自增的ID主键
    title = models.CharField(max_length=64,null=False,unique=True)
    publisher = models.ForeignKey(to="Publisher",on_delete=models.CASCADE)

    def __str__(self):
        return "<Book Object:{}",format(self.title)

# 作者
class Author(models.Model):
    id = models.AutoField(primary_key=True)# 自增的ID主键
    name = models.CharField(max_length=64,null=False,unique=True)
    book = models.ManyToManyField(to="Book")

    def __str__(self):
        return "<Author Object:{}",format(self.name)