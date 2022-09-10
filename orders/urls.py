"""orders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from store.views import ShopUpdate, SignUp, LogIn, ProductList, ProductInfoView, BasketView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop_update/', ShopUpdate.as_view(), name='shop_update'),
    path('sign_up/', SignUp.as_view(), name='sing_up'),
    path('login/', LogIn.as_view(), name='login'),
    # path('products/', ProductList.as_view(), name='product_list'),
    path('products_info/', ProductInfoView.as_view(), name='product_info'),
    path('basket/', BasketView.as_view(), name='basket'),
    # path('basket/', BasketView.as_view(), name='basket')
    # path('api/v1/', include('store.urls')),
]
