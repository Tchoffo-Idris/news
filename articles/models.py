from django.conf import settings
from django.db import models
from django.urls import reverse
from PIL import Image
from ckeditor.fields import RichTextField


class Article(models.Model):
    title = models.CharField(max_length=225)
    body = RichTextField()  # ← replaces TextField — gives users the rich editor
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to='articles/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            # Convert to RGB to ensure JPEG compatibility
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize if wider than 800px
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.LANCZOS)
            # Always save as compressed JPEG regardless of original format
            self.image.name = self.image.name.rsplit('.', 1)[0] + '.jpg'
            img.save(self.image.path, format='JPEG', optimize=True, quality=60)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.CharField(max_length=140)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("article_list")
