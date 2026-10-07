from django.urls import path
from trading.views import MomentumRankingView, RebalanceEventListView, TradingSignalListView

app_name = "trading"
urlpatterns = [
    path("rankings/", MomentumRankingView.as_view(), name="rankings"),
    path("signals/", TradingSignalListView.as_view(), name="signals"),
    path("rebalances/", RebalanceEventListView.as_view(), name="rebalances"),
]
