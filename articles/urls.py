from django.urls import path

from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleCreateView,
    ArticleByCategoryView,
    ArticleSearchView,
    EditorDeskView,
    BookmarkToggleView,
    ReadingListView,
)

urlpatterns = [
    path("<int:pk>/", ArticleDetailView.as_view(),
         name="article_detail"),
    path("<int:pk>/edit/", ArticleUpdateView.as_view(),
          name="article_edit"),
    path("<int:pk>/delete/", ArticleDeleteView.as_view(),
          name="article_delete"),
    path("", ArticleListView.as_view(),
         name="article_list"),
    path("new/", ArticleCreateView.as_view(),
         name="article_new"),
    path("category/<slug:slug>/", ArticleByCategoryView.as_view(),
         name="article_by_category"),
    path("search/", ArticleSearchView.as_view(),
         name="article_search"),
    path("desk/", EditorDeskView.as_view(),
         name="editor_desk"),
    path("<int:pk>/bookmark/", BookmarkToggleView.as_view(),
         name="article_bookmark"),
    path("reading-list/", ReadingListView.as_view(),
         name="reading_list"),
]
