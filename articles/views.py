from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Q, Count
from django.http import JsonResponse

from .models import Article, Category
from .forms import CommentForm

# Create your views here.


@method_decorator(never_cache, name="dispatch")
class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        # Identify the featured article (or latest as fallback)
        featured = Article.objects.filter(is_featured=True).first()
        if not featured:
            featured = Article.objects.order_by("-date").first()
        
        context["featured_article"] = featured
        
        # The list to display in secondary/sidebar areas (excluding the featured one)
        if featured:
            context["article_list"] = Article.objects.exclude(pk=featured.pk).order_by("-date")
        else:
            context["article_list"] = Article.objects.all().order_by("-date")
            
        return context


class ArticleByCategoryView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        return Article.objects.filter(category=self.category).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["active_category"] = self.category
        
        articles = self.get_queryset()
        # Use featured article if it's in this category, otherwise use latest in category
        featured = articles.filter(is_featured=True).first()
        if not featured:
            featured = articles.first()
            
        context["featured_article"] = featured
        if featured:
            context["article_list"] = articles.exclude(pk=featured.pk)
        else:
            context["article_list"] = articles
            
        return context


class ArticleSearchView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["categories"] = Category.objects.all()
        return context


class EditorDeskView(LoginRequiredMixin, TemplateView):
    template_name = "editor_desk.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        my_articles = Article.objects.filter(author=user).order_by("-date")
        total_articles = my_articles.count()
        total_comments = sum(a.comment_set.count() for a in my_articles)
        articles_with_counts = my_articles.annotate(comment_count=Count("comment"))
        most_commented = articles_with_counts.order_by("-comment_count").first()
        latest_article = my_articles.first()
        by_category = (
            my_articles.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        context["my_articles"] = articles_with_counts
        context["total_articles"] = total_articles
        context["total_comments"] = total_comments
        context["most_commented"] = most_commented
        context["latest_article"] = latest_article
        context["by_category"] = by_category
        return context


# ── ADDED: Bookmark toggle (AJAX) ──
class BookmarkToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
            user = request.user
            if user in article.bookmarks.all():
                article.bookmarks.remove(user)
                bookmarked = False
            else:
                article.bookmarks.add(user)
                bookmarked = True
            return JsonResponse({"bookmarked": bookmarked, "status": "success"})
        except Article.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Article not found"},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Failed to save bookmark"},
                status=500
            )


# ── ADDED: Reading list page ──
class ReadingListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "reading_list.html"

    def get_queryset(self):
        return self.request.user.bookmarked_articles.order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class CommentGet(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


class CommentPost(SingleObjectMixin, FormView):
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            comment = form.save(commit=False)
            comment.article = self.object
            comment.author = self.request.user
            comment.save()
            messages.success(self.request, "Comment posted successfully!")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, "Failed to post comment...")
            return self.form_invalid(form)

    def get_success_url(self):
        article = self.object
        return reverse("article_detail", kwargs={"pk": article.pk})


class ArticleDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = ("title", "body", "image", "category", "is_featured")
    template_name = "article_edit.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Article updated successfully!")
            return response
        except Exception as e:
            messages.error(self.request, "Failed to update article...")
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            form.fields.pop("is_featured", None)
        return form


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, "Article deleted successfully!")
            return response
        except Exception as e:
            messages.error(request, "Failed to delete article...")
            return redirect("article_list")


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"
    fields = ("title", "body", "image", "category", "is_featured")

    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, "Article published successfully!")
            return response
        except Exception as e:
            messages.error(self.request, "Failed to publish article...")
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            form.fields.pop("is_featured", None)
        return form
