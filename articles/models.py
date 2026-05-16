from django.conf import settings
from django.db import models
from django.urls import reverse
from PIL import Image
from ckeditor.fields import RichTextField
import re


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("article_by_category", kwargs={"slug": self.slug})


class Article(models.Model):
    title = models.CharField(max_length=225)
    body = RichTextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="bookmarked_articles",
        blank=True,
    )
    is_featured = models.BooleanField(default=False)

    def reading_time(self):
        plain_text = re.sub(r"<[^>]+>", "", self.body)
        word_count = len(plain_text.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def save(self, *args, **kwargs):
        if self.is_featured:
            # Ensure only one article is featured at a time
            Article.objects.filter(is_featured=True).exclude(pk=self.pk).update(is_featured=False)
        
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.LANCZOS)
            self.image.name = self.image.name.rsplit(".", 1)[0] + ".jpg"
            img.save(self.image.path, format="JPEG", optimize=True, quality=60)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-date"]


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
