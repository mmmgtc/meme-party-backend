from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Meme, UserProfile, Tag


class LoginRequestSerializer(serializers.Serializer):
    address = serializers.CharField(
        max_length=200)  # TODO: replace with a real validator
    signed = serializers.CharField(
        max_length=200)  # TODO: replace with a real validator


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'karma']
        read_only_fields = ['karma']


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'userprofile']
        read_only_fields = ['username']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class MemeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    poaster = UserSerializer(read_only=True)

    class Meta:
        model = Meme
        fields = [
            'id', 'title', 'image', 'upvotes', 'downvotes', 'description',
            'source', 'meme_lord', 'tags', 'poaster', 'created_at'
        ]
        read_only_fields = [
            'id', 'upvotes', 'downvotes', 'created_at', 'poaster'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        poast = Meme.objects.create(**validated_data)

        for t in tags:
            tag, created = Tag.objects.get_or_create(name=t['name'])
            poast.tags.add(tag)
        return poast

    def update(self, instance, validated_data):

        tags = validated_data.pop('tags', None)
        poast = instance

        poast.title = validated_data.get('title', poast.title)
        poast.image = validated_data.get('image', poast.image)
        poast.description = validated_data.get('description',
                                               poast.description)
        poast.source = validated_data.get('source', poast.source)
        poast.meme_lord = validated_data.get('meme_lord', poast.meme_lord)

        if tags is not None:
            poast.tags.clear()
            for t in tags:
                tag, created = Tag.objects.get_or_create(name=t['name'])
                poast.tags.add(tag)

        poast.save()

        return poast
