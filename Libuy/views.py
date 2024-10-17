from rest_framework import viewsets
from .models import Author, Auction, Book, Bid, Tags, User
from .serializers import AuthorSerializer, AuctionSerializer, BookSerializer, BidSerializer, TagsSerializer, \
    UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import logging
import json
import requests

logger = logging.getLogger(__name__)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                return Response({"message": "User registered successfully.", "token": token.key},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                return Response({"error": "An error occurred while creating the user."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username is None or password is None:
            return Response({'detail': 'Please provide both username and password.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)


class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
        }
        return Response(data)


class AddAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        book_name = request.data.get('book_name')
        author_name = request.data.get('author_name')
        date_start = request.data.get('date_start', timezone.now())
        date_end = request.data.get('date_end')
        price_start = request.data.get('price_start')

        if not book_name or not author_name or not date_end or not price_start:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        author_first_name, author_last_name = author_name.split(' ', 1) if ' ' in author_name else (author_name, "Unknown")
        author, _ = Author.objects.get_or_create(first_name=author_first_name, last_name=author_last_name)

        book, _ = Book.objects.get_or_create(title=book_name, author=author)

        auction_data = {
            "book": book.id,
            "date_start": date_start,
            "date_end": date_end,
            "price_start": price_start,
            "owner": request.user.id
        }

        serializer = AuctionSerializer(data=auction_data, context={'request': request})
        if serializer.is_valid():
            auction = serializer.save()

            tags = book_name.split(' ')
            for tag_name in tags:
                tag, _ = Tags.objects.get_or_create(name=tag_name)
                auction.tags.add(tag)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def add_auction_page(request):
    if request.method == "POST":
        token = request.COOKIES.get('access_token')
        if not token:
            return render(request, 'add_auction.html', {"error": "User is not authenticated."})

        book_name = request.POST.get('book_name')
        author_name = request.POST.get('author_name')
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        price_start = request.POST.get('price_start')

        tags = book_name.split()

        data = {
            "book_name": book_name,
            "author_name": author_name,
            "date_start": date_start,
            "date_end": date_end,
            "price_start": price_start,
            "tags": tags,
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.post('http://127.0.0.1:8000/api/auctions/add/', headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            return render(request, 'add_auction.html', {"success": "Auction added successfully!"})
        else:
            return render(request, 'add_auction.html', {"error": response.json()})

    return render(request, 'add_auction.html')