from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

from portfolio.models import Portfolio


class PortfolioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Portfolio
    template_name = "portfolio/portfolio_list.html"
    context_object_name = "portfolios"
    permission_required = "portfolio.view_portfolio"
    paginate_by = 20
