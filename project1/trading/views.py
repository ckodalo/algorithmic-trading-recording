from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django import forms
from django.views.generic import ListView

from trading.models import MomentumScore, RebalanceEvent, TradingSignal


class RankingFilterForm(forms.Form):
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    quintile = forms.ChoiceField(required=False, choices=[("", "All quintiles")] + [(str(i), str(i)) for i in range(1, 6)])


class SignalFilterForm(forms.Form):
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    signal_type = forms.ChoiceField(required=False, choices=[("", "All signals")] + TradingSignal.SIGNAL_TYPES)
    executed = forms.ChoiceField(required=False, choices=[("", "Any execution status"), ("yes", "Executed"), ("no", "Unexecuted")])


class RebalanceFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, choices=[("", "All statuses")] + list(RebalanceEvent._meta.get_field("execution_status").choices))


class FilteredListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    paginate_by = 20

    def get_queryset(self):
        self.filter_form = self.form_class(self.request.GET)
        queryset = super().get_queryset()
        if not self.filter_form.is_valid():
            return queryset.none()
        return self.filter_queryset(queryset, self.filter_form.cleaned_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filter_query"] = params.urlencode()
        return context


class MomentumRankingView(FilteredListView):
    model = MomentumScore
    permission_required = "trading.view_momentumscore"
    template_name = "trading/rankings.html"
    context_object_name = "scores"
    form_class = RankingFilterForm

    def filter_queryset(self, queryset, filters):
        self.calculation_date = filters["date"] or queryset.order_by("-calculation_date").values_list("calculation_date", flat=True).first()
        queryset = queryset.filter(calculation_date=self.calculation_date)
        if filters["quintile"]:
            queryset = queryset.filter(quintile=filters["quintile"])
        return queryset.select_related("stock").order_by("-momentum_score", "stock__ticker", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["calculation_date"] = getattr(self, "calculation_date", None)
        return context


class TradingSignalListView(FilteredListView):
    model = TradingSignal
    permission_required = "trading.view_tradingsignal"
    template_name = "trading/signals.html"
    context_object_name = "signals"
    form_class = SignalFilterForm

    def filter_queryset(self, queryset, filters):
        if filters["date"]:
            queryset = queryset.filter(signal_date=filters["date"])
        if filters["signal_type"]:
            queryset = queryset.filter(signal_type=filters["signal_type"])
        if filters["executed"]:
            queryset = queryset.filter(is_executed=filters["executed"] == "yes")
        return queryset.select_related("stock").order_by("-signal_date", "-created_at", "-pk")


class RebalanceEventListView(FilteredListView):
    model = RebalanceEvent
    permission_required = "trading.view_rebalanceevent"
    template_name = "trading/rebalances.html"
    context_object_name = "events"
    form_class = RebalanceFilterForm

    def filter_queryset(self, queryset, filters):
        if filters["status"]:
            queryset = queryset.filter(execution_status=filters["status"])
        return queryset.order_by("-date", "-created_at", "-pk")
