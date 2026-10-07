from django.urls import path
from portfolio.views import PortfolioDetailView, PortfolioListView

app_name = "portfolio"
urlpatterns = [
    path("", PortfolioListView.as_view(), name="list"),
    path("<int:pk>/", PortfolioDetailView.as_view(), name="detail"),
]
