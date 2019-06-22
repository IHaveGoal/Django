from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib
from me import forms, models
import logging, json
# Create your views here.

# 生成一个logger实例，专门用来记录日志
logger = logging.getLogger(__name__)

def register(requset):
    if requset.method == "POST":
        print(requset.POST)
        ret = {"status":0,"msg":""}
        form_obj = forms.RegForm(requset.POST)
        # print(form_obj)
        if form_obj.is_valid():
            form_obj.cleaned_data.pop("re_password")
            avatar_img = requset.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data,avatar=avatar_img)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    form_obj = forms.RegForm()
    return render(requset,"register.html",{"form_obj": form_obj})


# 校验用户名是否已被注册
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册！"
    return JsonResponse(ret)


# 注册
# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"

# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def login(request):
    if request.method == "POST":
        ret = {"status":0,"msg":""}
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确, 给用户做登录
                auth.login(request, user)  # 将登录用户赋值给 request.user
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")

# 获取自定义验证码图片的视图
def get_valid_img(request):
    # 自己生成一个图片
    from PIL import Image, ImageDraw, ImageFont
    import random

    # 获取随机颜色的函数
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成一个图片对象
    img_obj = Image.new(
        'RGB',
        (220, 35),
        get_random_color()
    )
    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件， 得到一个字体对象
    font_obj = ImageFont.truetype("static/font/kumo.ttf", 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(5):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20+40*i, 0), tmp, fill=get_random_color(), font=font_obj)

    print("".join(tmp_list))
    # 保存到session
    request.session["valid_code"] = "".join(tmp_list)
    # 加干扰线
    # width = 220  # 图片宽度（防止越界）
    # height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=get_random_color())
    #
    # # 加干扰点
    # for i in range(40):
    #     draw_obj.point((random.randint(0, width), random.randint(0, height)), fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=get_random_color())

    # 将生成的图片保存在磁盘上
    # with open("s10.png", "wb") as f:
    #     img_obj.save(f, "png")
    # # 把刚才生成的图片返回给页面
    # with open("s10.png", "rb") as f:
    #     data = f.read()

    # 不需要在硬盘上保存文件，直接在内存中加载就可以
    from io import BytesIO
    io_obj = BytesIO()
    # 将生成的图片数据保存在io对象中
    img_obj.save(io_obj, "png")
    # 从io对象里面取上一步保存的数据
    data = io_obj.getvalue()
    return HttpResponse(data)

# 注销
def logout(request):
    auth.logout(request)
    return redirect("/index/")

def index(request):
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})

def home(requset, username, *args):
    print(111)
    logger.debug("home视图取到用户名{}".format(username))
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        logger.warning("又有人访问不存在页面了...")
        return HttpResponse("404")
    blog = user.blog
    if not args:
        logger.debug("args没有接收到参数，默认走的是用户的个人博客页面！")
        # 我的文章列表
        article_list = models.Article.objects.filter(user=user)
    else:
        # 表示按照文章的分类或tag或日期归档来查询
        # args = ("category", "技术")
        if args[0] == 'category':
            article_list = models.Article.objects.filter(user=user).filter(category__title=args[1])
        elif args[0] == 'tag':
            article_list = models.Article.objects.filter(user=user).filter(tag__title=args[1])
        else:
            try:
                year, month = args[1].split('-')
                article_list = models.Article.objects.filter(user=user).filter(create_time__year=year,
                create_time__month=month)
            except Exception as e:
                logger.warning("请求访问的日期归档格式不正确！！！")
                logger.warning((str(e)))
                return HttpResponse('404')

    return render(requset, 'home.html', {
        "username": username, "blog": blog, "article_list": article_list,
    })

# 文章详情
def article_detail(request, username, pk):
    print(pk)
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        logger.warning('用户不存在')
        return HttpResponse("404")
    blog = user.blog
    # 找到当前的文章
    article_obj = models.Article.objects.filter(pk=pk).first()
    # 所有评论列表
    comment_list = models.Comment.objects.filter(article_id=pk)

    return render(request,"article_detail.html",{
            "username": username,
            "article": article_obj,
            "blog": blog, "comment_list": comment_list,
    })

# 点赞
from django.db.models import F

def up_down(request):
    print(request.POST)
    article_id=request.POST.get('article_id')
    is_up=json.loads(request.POST.get('is_up'))
    user=request.user
    response={"state":True}
    print("is_up",is_up)
    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)

    except Exception as e:
        response["state"]=False
        response["fisrt_action"]=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up

    return JsonResponse(response)


# 评论
def comment(request):

    print(request.POST)

    pid=request.POST.get("pid")
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    user_pk=request.user.pk
    response={}
    if not pid:  #根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content)
    else:
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content,parent_comment_id=pid)

    response["create_time"]=comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"]=comment_obj.content
    response["username"]=comment_obj.user.username

    return JsonResponse(response)


def comment_tree(request,article_id):

    ret=list(models.Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id"))
    print(ret)
    return JsonResponse(ret,safe=False)
