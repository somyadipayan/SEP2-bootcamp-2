from tools.workers import celery
from datetime import datetime, timedelta
from models import *
from tools.mailer import send_email
from flask import render_template
from celery.schedules import crontab

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(crontab(hour=10, minute=00), send_daily_email.s(), name='sending everyday at 10 AM')
    sender.add_periodic_task(30, send_daily_email.s(), name='every 30 seconds')


@celery.task
def send_daily_email():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    inactive_users = User.query.filter(User.lastLoggedIn < twenty_four_hours_ago).filter(User.role != "admin").all()

    for user in inactive_users:
        print(f"Sending email to {user.email}")
        # send email
        subject = "Daily Reminder"
        message = "You are getting this email as you have not logged in for 24 hours"
        html = render_template("daily_email.html", user=user,message=message)
        send_email(user.email, "Daily Reminder",body=html)


    return f"Emails sent to {len(inactive_users)} users"


def monthly_report():
    # We will send monthly report of orders to users
    
    pass

def send_order_summary(id):
    print(id)
    # We will send order summary to users
    pass