from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    karma = models.IntegerField(default=0)


class Tag(models.Model):
    name = models.CharField(max_length=50)

    # hack removing unique and testing just on the serializer
    # this is because drf doesn't handle nested serializers
    # and ensures unique during validation
    # since memes are the only way to create tags the meme serializer
    # now handles this

    def __str__(self):
        return f'Tag: {self.name}'


class Meme(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(max_length=512)
    upvoters = models.ManyToManyField(User, related_name='upvoters')
    downvoters = models.ManyToManyField(User, related_name='downvoters')
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    source = models.URLField(max_length=512, null=True)
    tags = models.ManyToManyField(Tag)  # where do tags come from?
    poaster = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    meme_lord = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'Meme: {self.title}'
