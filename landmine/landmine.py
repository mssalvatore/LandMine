from .alert_deduplicator import AlertDeduplicator
from .configuration.configuration import Configuration
from datetime import datetime
import logging
import re
import smtplib
import subprocess
import time

def send_email(config, to, message):
    logging.debug("Sending email to %s" % to);
    logging.debug("Message: \n%s" %message);
    s = smtplib.SMTP(host=config.smtp_server, port=config.smtp_port)
    s.starttls()
    s.login(config.smtp_username, config.smtp_password)

    from_address = ""

    try:
        s.sendmail(from_address, to, message)
    except SMTPException as e:
        logging.error("Caught SMTP exception: %s" % (str(e)))

def is_within_time_window(dtime, recipient):
    days_min = recipient.days_min
    days_max = recipient.days_max
    hours_min = recipient.hours_min
    hours_max = recipient.hours_max

    return is_within_days_window(dtime, days_min, days_max) \
            and is_within_hours_window(dtime, hours_min, hours_max)

def is_within_days_window(dtime, days_min, days_max):
    if days_min == '*':
        return True

    if days_min > days_max:
        return dtime.weekday() >= days_min or dtime.weekday() <= days_max

    return days_min <= dtime.weekday() and dtime.weekday() <= days_max

def is_within_hours_window(dtime, hours_min, hours_max):
    if hours_min == '*':
        return True

    if hours_min > hours_max:
        return dtime.hour >= hours_min or dtime.hour <= hours_max

    return hours_min <= dtime.hour and dtime.hour < hours_max

def email_alert(config, snort_alert):
    logging.info("Sending email with alert details")

    for r in config.alert_recipients:
        message = ("From: \n"
                   "To: " + r.email_address + "\n"
                   "Subject: " + config.email_subject + "\n\n"
                   + str(snort_alert))

        now = datetime.now()

        if is_within_time_window(now, r):
            send_email(config, r.email_address, message)

def email_threshold_exceeded_alert(config):
    logging.info("Email threshold exceeded, sending corresponding message.")
    for r in config.alert_recipients:
        message = ("From: \n"
                   "To: " + r.email_address + "\n"
                   "Subject: " + config.email_subject + "\n\n"
                   " Email alert threshold exceeded. See /var/log/snort/alert for more info.\n"
                  )

        now = datetime.now()

        if is_within_time_window(now, r):
            send_email(config, r.email_address, message)

def process_alert(config, alert_dedup, snort_alert):
    if alert_dedup.should_send_alert(snort_alert):
        email_alert(config, snort_alert)
    else:
        logging.warning("Not sending alerts: Sent count and sent time thresholds are exceeded. ")

def run():
    config = Configuration("./config.ini")

    alert_dedup = AlertDeduplicator(config.alert_threshold,
                                    config.get_alert_threshold_window_sec,
                                    config.suppress_duplicate_alerts)

    logging.basicConfig(format='%(asctime)s -- %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=config.landmine_log_path,
                        level=logging.DEBUG)

    f = subprocess.Popen(['tail', '-F', '-n', '0', config.snort_log_path],\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # TODO: On start, read network interface settings and build snort rule set,
    #       then restart snort. Use an ipvar to simplify ruleset generation:
    #       https://www.snort.org/faq/readme-variables
    while True:
        alert_lines = list()
        line = f.stdout.readline().decode("utf-8")
        while line != "\n":
            alert_lines.append(line)
            line = f.stdout.readline().decode("utf-8")

        logging.debug("Found snort alert:\n%s\n" % ("\n".join(alert_lines)))
        try:
            snort_alert = SnortAlert(alert_lines)
        except Exception as ex:
            #TODO: Send e-mail if snort alert is malformed
            pass
        else:
            process_alert(config, alert_dedup, snort_alert)

