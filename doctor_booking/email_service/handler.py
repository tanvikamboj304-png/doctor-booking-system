"""
Serverless email handler for Doctor Booking application.
Deploy with: serverless deploy
Test locally with: serverless offline
"""
import json
import boto3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@doctorbooking.com')


def _response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body),
    }


def _send_via_ses(to_email, subject, html_body, text_body):
    """Send email via AWS SES."""
    client = boto3.client('ses')
    client.send_email(
        Source=SENDER_EMAIL,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': text_body},
                'Html': {'Data': html_body},
            },
        },
    )


def send_booking_confirmation(event, context):
    """Send booking confirmation email to patient."""
    try:
        body = json.loads(event.get('body', '{}'))
        patient_email = body['patient_email']
        patient_name = body['patient_name']
        doctor_name = body['doctor_name']
        date = body['date']
        start_time = body['start_time']
        end_time = body['end_time']
        notes = body.get('notes', '')

        subject = f"✅ Appointment Confirmed — {date} at {start_time}"
        text_body = (
            f"Dear {patient_name},\n\n"
            f"Your appointment with Dr. {doctor_name} on {date} at {start_time}–{end_time} "
            f"has been confirmed.\n\n"
            f"{'Notes: ' + notes + chr(10) + chr(10) if notes else ''}"
            f"Thank you for using DocBook!\n"
        )
        html_body = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:#2b6cb0;color:white;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h1 style="margin:0;">🏥 DocBook</h1>
        </div>
        <div style="background:#f0fff4;border:1px solid #9ae6b4;padding:20px;border-radius:0 0 8px 8px;">
            <h2 style="color:#276749;">✅ Appointment Confirmed!</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>Your appointment details:</p>
            <table style="background:white;border-radius:8px;padding:15px;width:100%;">
                <tr><td><strong>Doctor:</strong></td><td>Dr. {doctor_name}</td></tr>
                <tr><td><strong>Date:</strong></td><td>{date}</td></tr>
                <tr><td><strong>Time:</strong></td><td>{start_time} – {end_time}</td></tr>
                {'<tr><td><strong>Notes:</strong></td><td>' + notes + '</td></tr>' if notes else ''}
            </table>
            <p style="margin-top:20px;color:#718096;font-size:0.85rem;">Thank you for using DocBook.</p>
        </div>
        </body></html>
        """
        _send_via_ses(patient_email, subject, html_body, text_body)
        return _response(200, {'message': 'Confirmation email sent successfully.'})
    except KeyError as e:
        return _response(400, {'error': f'Missing required field: {e}'})
    except Exception as e:
        return _response(500, {'error': str(e)})


def send_booking_cancellation(event, context):
    """Send cancellation email to patient."""
    try:
        body = json.loads(event.get('body', '{}'))
        patient_email = body['patient_email']
        patient_name = body['patient_name']
        doctor_name = body['doctor_name']
        date = body['date']
        start_time = body['start_time']

        subject = f"❌ Appointment Cancelled — {date} at {start_time}"
        text_body = (
            f"Dear {patient_name},\n\n"
            f"Your appointment with Dr. {doctor_name} on {date} at {start_time} "
            f"has been cancelled.\n\nYou can rebook at any time on DocBook.\n"
        )
        html_body = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:#e53e3e;color:white;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h1 style="margin:0;">🏥 DocBook</h1>
        </div>
        <div style="background:#fff5f5;border:1px solid #fc8181;padding:20px;border-radius:0 0 8px 8px;">
            <h2 style="color:#9b2c2c;">❌ Appointment Cancelled</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>Your appointment with Dr. <strong>{doctor_name}</strong> on <strong>{date}</strong> 
               at <strong>{start_time}</strong> has been cancelled.</p>
            <p>You can rebook anytime on DocBook.</p>
        </div>
        </body></html>
        """
        _send_via_ses(patient_email, subject, html_body, text_body)
        return _response(200, {'message': 'Cancellation email sent.'})
    except Exception as e:
        return _response(500, {'error': str(e)})


def send_doctor_notification(event, context):
    """Notify doctor of a new booking."""
    try:
        body = json.loads(event.get('body', '{}'))
        doctor_email = body['doctor_email']
        doctor_name = body['doctor_name']
        patient_name = body['patient_name']
        patient_email = body['patient_email']
        date = body['date']
        start_time = body['start_time']
        end_time = body['end_time']
        notes = body.get('notes', '')

        subject = f"📅 New Appointment — {patient_name} on {date}"
        text_body = (
            f"Dear Dr. {doctor_name},\n\n"
            f"{patient_name} ({patient_email}) has booked an appointment with you "
            f"on {date} at {start_time}–{end_time}.\n\n"
            f"{'Notes: ' + notes + chr(10) + chr(10) if notes else ''}"
            f"Log in to DocBook to manage your schedule.\n"
        )
        html_body = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:#2b6cb0;color:white;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h1 style="margin:0;">🏥 DocBook</h1>
        </div>
        <div style="background:#ebf4ff;border:1px solid #bee3f8;padding:20px;border-radius:0 0 8px 8px;">
            <h2 style="color:#2c5282;">📅 New Appointment Booked</h2>
            <p>Dear <strong>Dr. {doctor_name}</strong>,</p>
            <p>A new appointment has been scheduled:</p>
            <table style="background:white;border-radius:8px;padding:15px;width:100%;">
                <tr><td><strong>Patient:</strong></td><td>{patient_name} ({patient_email})</td></tr>
                <tr><td><strong>Date:</strong></td><td>{date}</td></tr>
                <tr><td><strong>Time:</strong></td><td>{start_time} – {end_time}</td></tr>
                {'<tr><td><strong>Notes:</strong></td><td>' + notes + '</td></tr>' if notes else ''}
            </table>
        </div>
        </body></html>
        """
        _send_via_ses(doctor_email, subject, html_body, text_body)
        return _response(200, {'message': 'Doctor notification sent.'})
    except Exception as e:
        return _response(500, {'error': str(e)})
