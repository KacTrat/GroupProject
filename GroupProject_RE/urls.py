from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Libuy.views import AuthorViewSet, AuctionViewSet, BookViewSet, BidViewSet, TagsViewSet, UserRegistrationView, \
    UserLoginAPIView, DashboardView, AddAuctionView, add_auction_page
from django.views.generic.base import TemplateView

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet)
router.register(r'books', BookViewSet)
router.register(r'bids', BidViewSet)
router.register(r'tags', TagsViewSet)
router.register(r'authors', AuthorViewSet)

urlpatterns = [
    path('', TemplateView.as_view(template_name="login.html"), name='login'),
    path('login/', TemplateView.as_view(template_name="login.html"), name='login'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register-page/', TemplateView.as_view(template_name="register.html"), name='register_page'),
    path('api/login/', UserLoginAPIView.as_view(), name='user_login'),
    path('dashboard/', TemplateView.as_view(template_name="dashboard.html"), name='dashboard'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard_api'),
    path('api/auctions/add/', AddAuctionView.as_view(), name='add_auction'),
    path('add-auction/', add_auction_page, name='add_auction_page'),
]
