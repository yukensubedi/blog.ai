from django.urls import path 
from . import views

urlpatterns = [ 
    path('', views.HomeView.as_view(), name='home'),
    path('topics/', views.GenerateBlogTopicsView.as_view(), name='generate_blog_topics'),
    path('sections/', views.GenerateBlogSectionView.as_view(), name='generate_blog_sections'),

    path('blog/', views.GenerateBlogView.as_view(), name='generate_blog'),
    path('blog/<int:pk>/', views.HistoryDetailView.as_view(), name='details'),
    path('blog/<str:slug>/edit', views.HistoryUpdateView.as_view(), name='edit'),
    path('blogs/', views.BlogListView.as_view(), name='list'),
    path('blogs/<str:slug>/', views.BlogDetailView.as_view(), name='blog-details'),
    path('blogs/<str:slug>/edit', views.BlogUpdateView.as_view(), name='blog-edit'),
    path('<pk>/delete', views.BlogDeleteView.as_view(), name='blog-delete'),
    path('tokenhistory/', views.TokenHistory.as_view(), name='token-history'),
    # path('<pk>/protect', views.BlogProtectView.as_view(), name='blog-protect'),

    path('ukn/', views.TestGenerateBlogTopicsView.as_view(), name='testgen'),

    path('regenerate/', views.Regenrate.as_view(), name='regen'),
    path('openai/', views.openai, name='openai'),
    path('test/', views.test, name='test')
]