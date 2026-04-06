"""
Admin Panel models for RoadAid Network.
PromoCode, Dispute, PlatformConfig, and EmergencyContact.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.mixins import TimestampMixin


class PromoCode(TimestampMixin, models.Model):
    """
    Promo / coupon code for discounts on service payments.
    """

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage')
        FLAT = 'flat', _('Flat Amount')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.TextField(blank=True)

    discount_type = models.CharField(
        max_length=12,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text=_('Percentage (0-100) or flat amount'),
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text=_('Minimum order amount required to apply this code'),
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text=_('Cap on discount for percentage type'),
    )

    usage_limit = models.PositiveIntegerField(
        default=0, help_text=_('0 = unlimited'),
    )
    times_used = models.PositiveIntegerField(default=0)

    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('promo code')
        verbose_name_plural = _('promo codes')

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()} {self.discount_value})"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, order_amount):
        """Return the discount amount for a given order total."""
        from decimal import Decimal
        order_amount = Decimal(str(order_amount))
        if order_amount < self.min_order_amount:
            return Decimal('0')
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = order_amount * (self.discount_value / Decimal('100'))
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = min(self.discount_value, order_amount)
        return discount.quantize(Decimal('0.01'))

    def use(self):
        self.times_used += 1
        self.save(update_fields=['times_used'])


class Dispute(TimestampMixin, models.Model):
    """
    Dispute raised by a user or helper for a service request.
    """

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        REVIEWING = 'reviewing', _('Under Review')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='disputes',
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disputes_raised',
    )
    description = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disputes_resolved',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute {self.id} – {self.get_status_display()}"

    def resolve(self, admin_user, notes: str = ''):
        from django.utils import timezone
        self.status = self.Status.RESOLVED
        self.resolved_by = admin_user
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_by', 'resolution_notes', 'resolved_at'])


class PlatformConfig(models.Model):
    """
    Key-value configuration for platform-wide settings.
    """
    key = models.CharField(max_length=100, unique=True, primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']
        verbose_name = _('platform config')

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default


class EmergencyContact(TimestampMixin, models.Model):
    """
    Emergency contacts for SOS feature.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone})"
