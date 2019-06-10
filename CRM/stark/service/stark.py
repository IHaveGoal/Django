from django.conf.urls import url
from django.urls import path
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from stark.utils.page import Pagination
from django.db.models.fields.related import ForeignKey, ManyToManyField

class ShowList(object):

    def __init__(self,config,data_list,request):
        # 即实例化的ModelStark对象
        self.config = config
        self.data_list = data_list
        self.request = request
        #分页
        current_page = int(self.request.GET.get("page",1))
        data_count = self.data_list.count()
        base_path = self.request.path
        # 调用分页模块，每页显示的数据
        self.pagination = Pagination(current_page,data_count,base_path,self.request.GET,per_page_num=3, pager_count=11)
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]

        # actions
        self.actions = self.config.new_actions() # [patch_init,]


    def get_filter_linktags(self):
        link_dic={}
        import copy
        # 遍历所有filter字段
        for filter_field in self.config.list_filter: # ["title","publish","authors",]
            params = copy.deepcopy(self.request.GET)
            # 当前键值
            cid=self.request.GET.get(filter_field,0)

            filter_field_obj=self.config.model._meta.get_field(filter_field)
            print(type(filter_field_obj))
            print(type(filter_field_obj.rel_class))

            if isinstance(filter_field_obj,ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                 data_list = filter_field_obj.rel_class.objects.all() # 【publish1,publish2...】
            else:
                 data_list = self.config.model.objects.all().values("pk",filter_field)
                 print("data_list",data_list)

            temp=[]
            # 处理 全部标签，存在就删除当前键值，恢复未选择状态
            if params.get(filter_field):
                del params[filter_field]
                temp.append("<a href='?%s'>全部</a>"%params.urlencode())
            else:
                temp.append("<a  class='active' href='#'>全部</a>")

            # 处理 数据标签
            for obj in data_list:
                if isinstance(filter_field_obj,ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                    # 是外键、多对多时，obj是字段对象，用到pk值
                    pk=obj.pk
                    text=str(obj)
                    params[filter_field] = pk
                else: # data_list= [{"pk":1,"title":"go"},....]
                    # 普通字段，obj是字典，用到字段的属性值
                    print("========")
                    pk=obj.get("pk")
                    text=obj.get(filter_field)
                    params[filter_field] = text

                _url = params.urlencode()
                if cid == str(pk) or cid == text:
                    # 选中状态，添加属性
                    link_tag="<a class='active' href='?%s'>%s</a>"%(_url,text)
                else:
                    link_tag = "<a href='?%s'>%s</a>" % (_url, text)
                temp.append(link_tag)

            link_dic[filter_field]=temp
        return link_dic

    def get_action_list(self):
        temp=[]
        for action in self.actions:
           temp.append({
               # 函数名、函数描述
               "name":action.__name__,
               "desc":action.short_description
           })  #  [{"name":""patch_init,"desc":"批量初始化"}]

        return temp

    def get_header(self):
        # 构建表头
        header_list = []
        for field in self.config.new_list_play():# [checkbox,"pk","name","age",edit ,deletes]   【checkbox ,"__str__", edit ,deletes】
            if callable(field):
                # 能调用即自定义函数，传入header=True，返回标题
                val = field(self.config, header=True)
                header_list.append(val)
            else:
                if field == "__str__":
                    # 为"__str__"说明只有默认选项，返回表名
                    header_list.append(self.config.model._meta.model_name.upper())
                else:
                    # 获取字段的verbose_name作为标题
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)
        return header_list

    def get_body(self):
        # 构建表单数据
        new_data_list = []
        # 只在页面显示数据范围处理数据
        for obj in self.page_data:
            temp = []
            for filed in self.config.new_list_play(): #[checkbox,"pk","name","age",edit ,deletes]  [checkbox ,"__str__", edit ,deletes]
                if callable(filed):
                    # 可以调用即为自定义函数，执行得到结果
                    val = filed(self.config, obj)
                else:
                    try:
                        # 字段对象
                        field_obj=self.config.model._meta.get_field(filed)
                        if isinstance(field_obj,ManyToManyField):
                            # 为多对多时取值方法
                            ret = getattr(obj,filed).all()
                            t=[]
                            for obj in ret:
                                t.append(str(obj))
                            val=",".join(t)

                        else:
                            val = getattr(obj, filed)
                            if filed in self.config.list_display_links:
                                # 通过self.config可以得到app名，表名，通过obj得到当前对象主键
                                _url = self.config.get_change_url(obj)
                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))
                    except Exception as e:
                        val = getattr(obj, filed)
                temp.append(val)

            new_data_list.append(temp)
        return new_data_list

class ModelStark(object):

    list_display = ["__str__"]
    list_display_links = []
    modelform_class = None
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self, model, site):
        self.model = model
        self.site = site

    # 编辑，删除，复选框
    def edit(self, obj=None, header=False):
        if header:
            return "操作"
        # return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)
        _url = self.get_change_url(obj)
        return mark_safe("<a href='%s'>编辑</a>" % _url)

    def deletes(self, obj=None, header=False):
        if header:
            return "操作"
        # return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)
        _url = self.get_delete_url(obj)
        return mark_safe("<a href='%s'>删除</a>" % _url)

    def checkbox(self, obj=None, header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')
        return mark_safe('<input class="choice_item" type="checkbox" name="selected_pk" value="%s">' % obj.pk)

    def new_list_play(self):
        # 默认添加复选框，编辑，删除
        temp=[]
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)
        return temp

    # 新动作
    def patch_delete(self, request, queryset):
        queryset.delete()
    patch_delete.short_description = "批量删除"

    def new_actions(self):
        temp=[]
        temp.append(ModelStark.patch_delete)
        temp.extend(self.actions)
        return temp

    # 模糊筛选
    def get_serach_conditon(self,request):
        key_word = request.GET.get("q","")
        self.key_word=key_word

        search_connection = Q()
        if key_word:
            # self.search_fields # ["title","price"]
            # 默认为且，修改为or
            search_connection.connector = "or"
            for search_field in self.search_fields:
                # 模糊筛选
                search_connection.children.append((search_field + "__contains", key_word))
        return search_connection

    # filter筛选
    def get_filter_condition(self,request):
        filter_condition=Q()

        for filter_field,val in request.GET.items():
            if filter_field in self.list_filter:
                filter_condition.children.append((filter_field,val))
        return filter_condition


    def get_modelform_class(self):
        if not self.modelform_class:
            from django.forms import ModelForm
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
                    labels = {
                        ""
                    }
            return ModelFormDemo
        else:
            return self.modelform_class

    def add_view(self, request):
        ModelFormDemo = self.get_modelform_class()
        form = ModelFormDemo()

        for bfield in form:
            print(bfield.field) # 字段对象
            print("name",bfield.name)  # 字段名（字符串）
            print(type(bfield.field)) # 字段类型
            from django.forms.models import ModelChoiceField
            if isinstance(bfield.field,ModelChoiceField):
                bfield.is_pop=True

                print("=======>",bfield.field.queryset.model) # 一对多或者多对多字段的关联模型表

                related_model_name=bfield.field.queryset.model._meta.model_name
                related_app_label=bfield.field.queryset.model._meta.app_label

                _url=reverse("%s_%s_add"%(related_app_label,related_model_name))
                bfield.url=_url+"?pop_res_id=id_%s"%bfield.name


        if request.method=="POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                obj=form.save()
                pop_res_id=request.GET.get("pop_res_id")

                if pop_res_id:
                    res ={"pk":obj.pk,"text":str(obj),"pop_res_id":pop_res_id}
                    return render(request,"pop.html",{"res":res})
                else:
                    return redirect(self.get_list_url())
        return render(request,"add_view.html",locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method=="POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)

        return render(request,"delete_view.html",locals())

    def change_view(self, request, id):
        ModelFormDemo = self.get_modelform_class()
        edit_obj = self.model.objects.filter(pk=id).first()

        if request.method=="POST":
            form = ModelFormDemo(request.POST,instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, "add_view.html", locals())

        form = ModelFormDemo(instance=edit_obj)
        return render(request, "change_view.html", locals())

    def list_view(self, request):
        if request.method=="POST":  # action
            print("POST:",request.POST)
            action=request.POST.get("action") # patch_init
            selected_pk=request.POST.getlist("selected_pk")
            action_func=getattr(self,action)
            queryset=self.model.objects.filter(pk__in=selected_pk)
            ret=action_func(request,queryset)

        # 获取serach的Q对象
        search_connection=self.get_serach_conditon(request)

        # 获取filter构建Q对象
        filter_condition=self.get_filter_condition(request)

        # 筛选获取当前表所有数据
        data_list=self.model.objects.all().filter(search_connection).filter(filter_condition)            # 【obj1,obj2,....】

        # 按这ShowList展示页面
        showlist=ShowList(self,data_list,request)

        # 构建一个查看URL
        add_url=self.get_add_url()
        return render(request, "list_view.html", locals())

    def get_urls2(self):
        temp = []
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        temp.append(path("add/", self.add_view, name="%s_%s_add" % (app_label, model_name)))
        temp.append(path("(\d+)/delete/", self.delete_view, name="%s_%s_delete" % (app_label, model_name)))
        temp.append(path("(\d+)/change/", self.change_view, name="%s_%s_change" % (app_label, model_name)))
        temp.append(path("", self.list_view, name="%s_%s_list" % (app_label, model_name)))

        return temp

    def get_add_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_add" % (app_label, model_name))
        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_change_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_list_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_list" % (app_label, model_name))
        return _url

    @property
    def urls2(self):
        return self.get_urls2(),None,None


class StarkSite(object):

    def __init__(self):
        self._registry = {}

    def register(self, model, stark_class=None):
        if stark_class==None:
            stark_class = ModelStark
        self._registry[model] = stark_class(model, self)

    def get_urls(self):
        temp = []
        for model,stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            # 分发增删改查
            temp.append(path("%s/%s/"%(app_label,model_name),stark_class_obj.urls2))
        return temp

    @property
    def urls(self):
        return self.get_urls(),None,None

site = StarkSite()