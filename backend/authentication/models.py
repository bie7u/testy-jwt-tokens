from django.db import models
from django.contrib.auth.models import User
import uuid


class DiagnosticExchangeCode(models.Model):
    """
    Short-lived code used to transfer diagnostic tokens from the intranet
    frontend to the customer frontend. A staff member uses this to log in
    as a customer for diagnostic purposes.

    Both the customer's tokens and the staff member's access token are stored
    so that the customer frontend can authenticate as the customer while also
    carrying the staff member's JWT for server-side audit logging.
    """
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    staff_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='diagnostic_codes_issued'
    )
    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='diagnostic_codes_received'
    )
    customer_access_token = models.TextField()
    customer_refresh_token = models.TextField()
    # Staff member's access token so the customer frontend can also carry
    # the staff identity as a session cookie for audit purposes.
    staff_access_token = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'diagnostic_exchange_codes'

    def __str__(self):
        return f"ExchangeCode({self.code}) staff={self.staff_user_id} customer={self.customer_user_id}"
