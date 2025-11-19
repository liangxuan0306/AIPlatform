from django.urls import path
from . import views
from .views import tools_view
urlpatterns = [
    path('', views.home, name='home'),  # http://127.0.0.1:8000/ 頁面
    path('intro/', views.intro, name='intro'),
    path('tools/', tools_view, name='tools'),
    path('recommend/', views.recommend, name='recommend'),  # 第一頁（封面）
    path('contact/', views.contact, name='contact'),    
    path('recommend/step1/', views.recommend1, name='recommend1'),  # 第二頁
    path('recommend/step2/', views.recommend2, name='recommend2'),  # 第三頁
    path('recommend/result/', views.recommend_result, name='recommend_result'),  # 結果
]

