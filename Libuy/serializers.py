from rest_framework import serializers
from .models import Author, Auction, Book, Bid, Tags, User
from rest_framework.serializers import ModelSerializer, CharField, ValidationError


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class AuctionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Auction
        fields = '__all__'

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class BidSerializer(serializers.ModelSerializer):
    auction = AuctionSerializer()

    class Meta:
        model = Bid
        fields = '__all__'


class UserRegistrationSerializer(ModelSerializer):
    password = CharField(write_only=True)
    password_confirm = CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm')

    def validate(self, data):
        if 'password' not in data or 'password_confirm' not in data:
            raise ValidationError("Both password fields are required.")
        if data['password'] != data['password_confirm']:
            raise ValidationError("Passwords do not match.")
        if len(data['password']) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if User.objects.filter(username=data['username']).exists():
            raise ValidationError("A user with that username already exists.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user



