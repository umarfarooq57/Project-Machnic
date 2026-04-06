"""
User services — email, OTP, and verification helpers.
"""
import random
import string
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def _generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(user) -> str:
    """
    Create a verification code and email it to the user.
    Returns the generated code (for tests).
    """
    from apps.users.models import UserVerification

    code = _generate_code()
    UserVerification.objects.create(
        user=user,
        verification_type=UserVerification.VerificationType.EMAIL,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=15),
    )

    send_mail(
        subject='RoadAid – Verify Your Email',
        message=f'Your verification code is: {code}\n\nThis code expires in 15 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@roadaid.com',
        recipient_list=[user.email],
        fail_silently=True,
    )
    return code


def send_password_reset_email(user) -> str:
    """
    Create a password-reset code and email it.
    """
    from apps.users.models import UserVerification

    code = _generate_code()
    UserVerification.objects.create(
        user=user,
        verification_type=UserVerification.VerificationType.PASSWORD_RESET,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=15),
    )

    send_mail(
        subject='RoadAid – Password Reset',
        message=f'Your password reset code is: {code}\n\nThis code expires in 15 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@roadaid.com',
        recipient_list=[user.email],
        fail_silently=True,
    )
    return code


def send_otp_sms(user, phone: str = None) -> str:
    """
    Send OTP via SMS (placeholder — swap in Twilio / provider).
    In development, prints to console.
    """
    from apps.users.models import UserVerification

    code = _generate_code()
    UserVerification.objects.create(
        user=user,
        verification_type=UserVerification.VerificationType.PHONE,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    target_phone = phone or user.phone
    # ── Production: replace with Twilio / SNS ──
    # client = Client(TWILIO_SID, TWILIO_TOKEN)
    # client.messages.create(body=f"Your RoadAid code: {code}", to=target_phone, from_=TWILIO_NUMBER)
    import logging
    logger = logging.getLogger('apps.users')
    logger.info(f"[OTP] Sending code {code} to {target_phone}")

    return code


def verify_otp(user, code: str, verification_type: str = 'phone') -> bool:
    """
    Validate OTP code against the latest unused verification record.
    Returns True on success and marks the record as used.
    """
    from apps.users.models import UserVerification

    record = (
        UserVerification.objects
        .filter(user=user, verification_type=verification_type, is_used=False)
        .order_by('-created_at')
        .first()
    )

    if record is None:
        return False

    if not record.is_valid:
        return False

    if record.code != code:
        return False

    record.is_used = True
    record.save(update_fields=['is_used'])

    # Mark user as verified if email or phone verification
    if verification_type in ('email', 'phone'):
        user.is_verified = True
        user.save(update_fields=['is_verified'])

    return True
