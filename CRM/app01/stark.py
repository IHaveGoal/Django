from stark.service.stark import site, ModelStark
from .models import *
from django.forms import ModelForm
from django.shortcuts import HttpResponse

class BookModelForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"

        labels = {
            "title":"书籍名",
            "price":"价格"
        }

class BookConfig(ModelStark):

    list_display = ["title","price","publishDate","publish","authors"]
    list_display_links = ["title"]
    modelform_Class = BookModelForm
    search_fields = ["title","price"]

    def patch_init(self,request,queryset):
        queryset.update(price=166)
        return HttpResponse("批量初始化")
    patch_init.short_description = "批量初始化"
    actions = [patch_init]

    list_filter = ["title", "price", "authors"]

site.register(Book, BookConfig)
site.register(Publish)
site.register(Author)
site.register(AuthorDetail)