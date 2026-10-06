from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Portfolio


class PortfolioListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="test-password")
        self.url = reverse("portfolio:list")

    def grant_access(self):
        self.user.user_permissions.add(
            Permission.objects.get(content_type__app_label="portfolio", codename="view_portfolio")
        )
        self.client.force_login(self.user)

    def test_anonymous_user_must_sign_in(self):
        self.assertRedirects(self.client.get(self.url), "/accounts/login/?next=/portfolios/")

    def test_user_without_permission_cannot_read_portfolios(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_empty_state(self):
        self.grant_access()
        self.assertContains(self.client.get(self.url), "No portfolios yet")

    def test_portfolio_values_status_and_escaping(self):
        self.grant_access()
        Portfolio.objects.create(
            name="Growth", description="<script>alert(1)</script>",
            initial_cash="10000", current_cash="1250.50", total_value="12000.25",
        )
        Portfolio.objects.create(
            name="Retired", initial_cash="100", current_cash="100",
            total_value="100", is_active=False,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "$12,000.25")
        self.assertContains(response, "$1,250.50")
        self.assertContains(response, "Inactive")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")

    def test_login_returns_to_portfolios(self):
        self.grant_access()
        self.client.logout()
        self.assertRedirects(
            self.client.post(reverse("login"), {"username": "viewer", "password": "test-password"}),
            self.url,
        )

    def test_pagination(self):
        self.grant_access()
        Portfolio.objects.bulk_create([
            Portfolio(name=f"Portfolio {i:02}", initial_cash=100, current_cash=100)
            for i in range(21)
        ])
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["portfolios"]), 20)
        self.assertContains(response, "Next")
        self.assertContains(self.client.get(self.url + "?page=2"), "Portfolio 20")
