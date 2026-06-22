from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _get_client():
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _format_phone(phone: str) -> str:
    """
    Converts any Indian phone number to WhatsApp E.164 format.
    Works with:  9876543210 / +919876543210 / 09876543210
    """
    phone = phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = phone[1:]
    if not phone.startswith('+'):
        phone = '+91' + phone if len(phone) == 10 else '+' + phone
    return f'whatsapp:{phone}'


SPORT_NAMES = {
    'football-5v5':   'Football 5v5',
    'football-10v10': 'Football 10v10',
    'futsal':         'Futsal',
    'snooker':        'Snooker',
    'carrom':         'Carrom',
    'ping-pong':      'Ping Pong',
    'vr':             'VR Gaming',
}


def send_booking_confirmation(booking_data: dict) -> bool:
    """Send WhatsApp confirmation after a successful booking."""
    try:
        client = _get_client()
        to     = _format_phone(booking_data['phone'])
        sport  = SPORT_NAMES.get(booking_data['turf_type'], booking_data['turf_type'])

        message = (
            f"*Booking Confirmed - BookMyTurf*\n\n"
            f"Hey {booking_data['name']}! Your session is locked in.\n\n"
            f"Sport: {sport}\n"
            f"Date: {booking_data['date']}\n"
            f"Slot: {booking_data['time_slot']}\n\n"
            f"See you on the field!\n"
            f"BookMyTurf"
        )

        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to,
            body=message,
        )

        logger.info(f"WhatsApp confirmation sent to {booking_data['phone']}")
        return True

    except Exception as e:
        logger.error(f"WhatsApp confirmation failed: {e}")
        return False


def send_booking_reminder(booking_data: dict) -> bool:
    """Send a reminder 1 hour before the session."""
    try:
        client = _get_client()
        to     = _format_phone(booking_data['phone'])
        sport  = SPORT_NAMES.get(booking_data['turf_type'], booking_data['turf_type'])

        message = (
            f"*Reminder - BookMyTurf*\n\n"
            f"Hey {booking_data['name']}! Your session starts in 1 hour.\n\n"
            f"Sport: {sport}\n"
            f"Date: {booking_data['date']}\n"
            f"Slot: {booking_data['time_slot']}\n\n"
            f"Get warmed up!\n"
            f"BookMyTurf"
        )

        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to,
            body=message,
        )

        logger.info(f"WhatsApp reminder sent to {booking_data['phone']}")
        return True

    except Exception as e:
        logger.error(f"WhatsApp reminder failed: {e}")
        return False


def send_cancellation_notice(booking_data: dict) -> bool:
    """Send WhatsApp message when a booking is cancelled."""
    try:
        client = _get_client()
        to     = _format_phone(booking_data['phone'])
        sport  = SPORT_NAMES.get(booking_data['turf_type'], booking_data['turf_type'])

        message = (
            f"*Booking Cancelled - BookMyTurf*\n\n"
            f"Hey {booking_data['name']}, your booking has been cancelled.\n\n"
            f"Sport: {sport}\n"
            f"Date: {booking_data['date']}\n"
            f"Slot: {booking_data['time_slot']}\n\n"
            f"To book again: bookmyturf.com\n"
            f"BookMyTurf"
        )

        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to,
            body=message,
        )

        logger.info(f"WhatsApp cancellation sent to {booking_data['phone']}")
        return True

    except Exception as e:
        logger.error(f"WhatsApp cancellation failed: {e}")
        return False