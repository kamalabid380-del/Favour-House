from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("shop/<slug:slug>/", views.shop, name="category"),
    path("piece/<slug:slug>/", views.product_detail, name="product"),
    path("journal/", views.journal_list, name="journal"),
    path("journal/<slug:slug>/", views.journal_detail, name="journal_post"),
]

handler404 = "sitecontent.views.custom_404"
