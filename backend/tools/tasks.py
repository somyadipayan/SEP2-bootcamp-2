from tools.workers import celery
from datetime import datetime, timedelta
from models import *
from tools.mailer import send_email
from flask import render_template
from celery.schedules import crontab

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(crontab(hour=10, minute=00), send_daily_email.s(), name='sending everyday at 10 AM')
    # sender.add_periodic_task(30, send_daily_email.s(), name='every 30 seconds')
    sender.add_periodic_task(20, monthly_report.s(), name='every 20 seconds')
    # sender.add_periodic_task(crontab(day_of_month=1 ,hour=8, minute=00), monthly_report.s(), name='sending monthly at 8 AM')


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

@celery.task
def monthly_report():
    # We will send monthly report of orders to users
    users = User.query.filter_by(role="user").all()
    one_month_ago = datetime.now() - timedelta(days=30)

    for user in users:
        # getting user orders from past month
        user_orders = Order.query.filter_by(user_id=user.id).filter(Order.order_date > one_month_ago).all()
        order_details = []
        total_amount_spent = 0

        for order in user_orders:
            order_details.append({
                "order_date": order.order_date,
                "product_names": [item.product.name for item in order.order_items],
                "total_order_value": order.total_amount
            })
            total_amount_spent += order.total_amount

        html = render_template("monthly_report.html", user=user, order_details=order_details, total_amount_spent=total_amount_spent)

        send_email(user.email, "Monthly Report", html)
    return f"Monthly report sent to {len(users)} users"

def send_order_summary(id):
    print(id)
    # We will send order summary to users
    pass