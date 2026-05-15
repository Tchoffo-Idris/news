from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Q, Count

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
        return context


class ArticleByCategoryView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        return Article.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["active_category"] = self.category
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

        # All articles by this author
        my_articles = Article.objects.filter(author=user).order_by("-date")

        # Stats
        total_articles = my_articles.count()
        total_comments = sum(a.comment_set.count() for a in my_articles)

        # Articles with comment counts
        articles_with_counts = my_articles.annotate(
            comment_count=Count("comment")
        )

        # Most commented article
        most_commented = articles_with_counts.order_by("-comment_count").first()

        # Latest article
        latest_article = my_articles.first()

        # Articles by category breakdown
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
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

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
    fields = ("title", "body", "image", "category")
    template_name = "article_edit.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"
    fields = ("title", "body", "image", "category")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
