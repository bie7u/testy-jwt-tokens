from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
import json


class LoginViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staffuser', password='pass123', is_staff=True
        )
        self.customer = User.objects.create_user(
            username='customer1', password='pass123', is_staff=False
        )

    def test_login_sets_cookies(self):
        """Successful login should set HTTP-only access and refresh cookies."""
        resp = self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'staffuser', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access_token', resp.cookies)
        self.assertIn('refresh_token', resp.cookies)
        self.assertTrue(resp.cookies['access_token']['httponly'])
        self.assertTrue(resp.cookies['refresh_token']['httponly'])
        data = resp.json()
        self.assertEqual(data['user']['username'], 'staffuser')

    def test_login_invalid_credentials(self):
        resp = self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'staffuser', 'password': 'wrong'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_login_require_staff_rejects_customer(self):
        resp = self.client.post(
            reverse('auth-login') + '?require_staff=true',
            data=json.dumps({'username': 'customer1', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_login_require_staff_allows_staff(self):
        resp = self.client.post(
            reverse('auth-login') + '?require_staff=true',
            data=json.dumps({'username': 'staffuser', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)


class MeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def _login(self):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'testuser', 'password': 'pass123'}),
            content_type='application/json',
        )

    def test_me_requires_auth(self):
        resp = self.client.get(reverse('auth-me'))
        self.assertEqual(resp.status_code, 401)

    def test_me_returns_user(self):
        self._login()
        resp = self.client.get(reverse('auth-me'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['username'], 'testuser')


class UserListViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='pass', is_staff=True
        )
        self.customer = User.objects.create_user(
            username='customer', password='pass', is_staff=False
        )

    def _login_as(self, username):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': username, 'password': 'pass'}),
            content_type='application/json',
        )

    def test_customer_cannot_list_users(self):
        self._login_as('customer')
        resp = self.client.get(reverse('auth-users'))
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_list_customers(self):
        self._login_as('staff')
        resp = self.client.get(reverse('auth-users'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        usernames = [u['username'] for u in data]
        self.assertIn('customer', usernames)
        self.assertNotIn('staff', usernames)


class DiagnosticLoginTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='pass', is_staff=True
        )
        self.customer = User.objects.create_user(
            username='customer', password='pass', is_staff=False
        )

    def _login_as_staff(self):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'staff', 'password': 'pass'}),
            content_type='application/json',
        )

    def test_diagnostic_login_returns_code(self):
        self._login_as_staff()
        resp = self.client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('code', data)
        self.assertEqual(data['customer']['username'], 'customer')

    def test_customer_cannot_use_diagnostic_login(self):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'customer', 'password': 'pass'}),
            content_type='application/json',
        )
        resp = self.client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_exchange_code_sets_cookies(self):
        self._login_as_staff()
        diag_resp = self.client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        code = diag_resp.json()['code']

        # Use a fresh client to simulate customer frontend (no staff cookies)
        from django.test import Client
        fresh_client = Client()
        exchange_resp = fresh_client.post(
            reverse('auth-exchange'),
            data=json.dumps({'code': code}),
            content_type='application/json',
        )
        self.assertEqual(exchange_resp.status_code, 200)
        data = exchange_resp.json()
        self.assertEqual(data['customer']['username'], 'customer')
        self.assertEqual(data['staff']['username'], 'staff')
        self.assertTrue(data['diagnostic'])
        self.assertIn('access_token', exchange_resp.cookies)
        self.assertIn('refresh_token', exchange_resp.cookies)
        # Staff token cookie must also be set
        self.assertIn('staff_access_token', exchange_resp.cookies)

    def test_exchange_code_sets_session_cookies(self):
        """Diagnostic cookies must be session cookies (no max_age)."""
        self._login_as_staff()
        diag_resp = self.client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        code = diag_resp.json()['code']

        from django.test import Client
        fresh_client = Client()
        exchange_resp = fresh_client.post(
            reverse('auth-exchange'),
            data=json.dumps({'code': code}),
            content_type='application/json',
        )
        self.assertEqual(exchange_resp.status_code, 200)
        # Session cookies have max_age == '' (not set), distinguishing them
        # from persistent cookies where max_age is a positive integer.
        for cookie_name in ('access_token', 'refresh_token', 'staff_access_token'):
            max_age = exchange_resp.cookies[cookie_name]['max-age']
            self.assertEqual(
                max_age, '',
                msg=f"{cookie_name} should be a session cookie (no max-age), got {max_age!r}",
            )

    def test_exchange_code_is_single_use(self):
        self._login_as_staff()
        diag_resp = self.client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        code = diag_resp.json()['code']

        from django.test import Client
        c1 = Client()
        c2 = Client()
        r1 = c1.post(
            reverse('auth-exchange'),
            data=json.dumps({'code': code}),
            content_type='application/json',
        )
        r2 = c2.post(
            reverse('auth-exchange'),
            data=json.dumps({'code': code}),
            content_type='application/json',
        )
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 400)  # second use should fail


class DiagnosticInfoViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='pass', is_staff=True
        )
        self.customer = User.objects.create_user(
            username='customer', password='pass', is_staff=False
        )

    def _do_diagnostic_exchange(self):
        """Login as staff, create a diagnostic code and exchange it. Returns the exchange client."""
        staff_client = self.client
        staff_client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'staff', 'password': 'pass'}),
            content_type='application/json',
        )
        diag_resp = staff_client.post(
            reverse('auth-diagnostic-login'),
            data=json.dumps({'customer_id': self.customer.id}),
            content_type='application/json',
        )
        code = diag_resp.json()['code']

        from django.test import Client
        customer_client = Client()
        customer_client.post(
            reverse('auth-exchange'),
            data=json.dumps({'code': code}),
            content_type='application/json',
        )
        return customer_client

    def test_diagnostic_info_returns_staff(self):
        """After exchange, GET /diagnostic-info/ returns the staff user's info."""
        customer_client = self._do_diagnostic_exchange()
        resp = customer_client.get(reverse('auth-diagnostic-info'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['staff']['username'], 'staff')
        self.assertTrue(data['diagnostic'])

    def test_diagnostic_info_without_cookie_returns_404(self):
        """Without a staff_access_token cookie there is no diagnostic session."""
        from django.test import Client
        fresh_client = Client()
        resp = fresh_client.get(reverse('auth-diagnostic-info'))
        self.assertEqual(resp.status_code, 404)

    def test_regular_login_does_not_set_staff_cookie(self):
        """A regular (non-diagnostic) login must NOT set the staff_access_token cookie."""
        resp = self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'customer', 'password': 'pass'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('staff_access_token', resp.cookies)

    def test_regular_login_sets_persistent_cookies(self):
        """Regular login cookies must carry an explicit max_age (persistent)."""
        resp = self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'customer', 'password': 'pass'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        for cookie_name in ('access_token', 'refresh_token'):
            max_age = resp.cookies[cookie_name]['max-age']
            self.assertNotEqual(
                max_age, '',
                msg=f"Regular login {cookie_name} should be persistent (has max-age), got {max_age!r}",
            )
            self.assertGreater(int(max_age), 0)



class RefreshTokenViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')

    def test_refresh_issues_new_access_token(self):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'user', 'password': 'pass'}),
            content_type='application/json',
        )
        resp = self.client.post(reverse('auth-refresh'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access_token', resp.cookies)

    def test_refresh_without_cookie_returns_401(self):
        resp = self.client.post(reverse('auth-refresh'))
        self.assertEqual(resp.status_code, 401)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')

    def test_logout_clears_cookies(self):
        self.client.post(
            reverse('auth-login'),
            data=json.dumps({'username': 'user', 'password': 'pass'}),
            content_type='application/json',
        )
        resp = self.client.post(reverse('auth-logout'))
        self.assertEqual(resp.status_code, 200)
        # After logout the access_token cookie should have max_age=0 (cleared)
        self.assertEqual(resp.cookies['access_token']['max-age'], 0)
