#!/usr/bin/env python3

from configuration.configuration import Configuration
import datetime
import logging
import re
import smtplib
import subprocess
import time

config = Configuration("./config.ini")

rule_id_regex = re.compile(r"\[\d+:(\d+):\d+\]")
def parse_rule_id(alert_lines):
    matches = rule_id_regex.search(alert_lines[0]);
    if matches:
        return matches.group(1)

    return "";

msg_regex = re.compile(r"\[\*\*\] \[.*\] (.*) \[\*\*\]")
def parse_alert_msg(alert_lines):
    matches = msg_regex.search(alert_lines[0]);
    if matches:
        return matches.group(1)

    return "";

def parse_timestamp(alert_lines):
    return alert_lines[2].split(' ')[0]

def parse_packet_ip_port_direction(alert_lines):
    split_line = alert_lines[2].split(' ');
    src = split_line[1]
    direction = split_line[2]
    destination = split_line[3]
    return src + " " + direction + " " + destination;

def parse_protocol(alert_lines):
    return alert_lines[3].split(' ')[0];

def send_email(to, message):
    logging.debug("Sending email to %s" % to);
    logging.debug("Message: \n%s" %message);
    s = smtplib.SMTP(host=config.get_smtp_server(), port=config.get_smtp_port())
    s.starttls()
    s.login(config.get_smtp_username(), config.get_smtp_password())

    from_address = ""

    try:
        s.sendmail(from_address, to, message)
    except SMTPException as e:
        logging.error("Caught SMTP exception: %s" % (str(e)))

def within_time_window(atime, recipient):
    days_min = recipient.days_min
    days_max = recipient.days_max
    hours_min = recipient.hours_min
    hours_max = recipient.hours_max

    if days_min == '*':
        if hours_min == '*':
            return True
        if hours_min <= atime.hour and atime.hour <= hours_max):
            return True

    if (hours_min == '*' and
       (days_min <= atime.weekday() and atime.weekday() <= days_max)):
            return True

    if ((days_min <= atime.weekday() and atime.weekday() <= days_max) and
        (hours_min <= atime.hour and atime.hour <= hours_max)):
            return True

    return False

email_address = ""
sms_email_address = ""
def email_alert(alert_lines):
    logging.info("Sending email with alert details")
    timestamp = parse_timestamp(alert_lines)
    rule_id = parse_rule_id(alert_lines)
    alert_msg = parse_alert_msg(alert_lines)
    protocol = parse_protocol(alert_lines)
    packet_header_info = parse_packet_ip_port_direction(alert_lines)

    for r in config.get_alert_recipients():
        message = ("From: \n"
                   "To: " + r.email_address + "\n"
                   "Subject: " + config.get_email_subject() + "\n\n"
                   " Timestamp: " + timestamp + "\n"
                   " Rule ID:" + rule_id + "\n"
                   " Message: " + alert_msg + "\n"
                   " Protocol: " + protocol + "\n"
                   " Packet Data:" + packet_header_info + "\n"
                  )

        now = datetime.datetime.now()

        if within_time_window(now, r):
            send_email(r.email_address, message)

def email_threshold_exceeded_alert():
    logging.info("Email threshold exceeded, sending corresponding message.")
    for r in config.get_alert_recipients():
        message = ("From: \n"
                   "To: " + r.email_address + "\n"
                   "Subject: " + config.get_email_subject() + "\n\n"
                   " Email alert threshold exceeded. See /var/log/snort/alert for more info.\n"
                  )

        now = datetime.datetime.now()

        if within_time_window(now, r):
            send_email(r.email_address, message)

last_sent_time = 0
last_sent_count = 0
def process_alert(alert_text):
    #TODO: Add logic for suppressing duplicate alerts within the alert_threshold_window
    global last_sent_time
    global last_sent_count
    alert_lines = alert_text.split('\n');
    if (time.time() - config.get_alert_threshold_window_sec()) > last_sent_time:
        last_sent_count = 0

    if last_sent_count < config.get_alert_threshold():
        email_alert(alert_lines)
        last_sent_count = last_sent_count + 1
        last_sent_time = time.time()
    elif last_sent_count == config.get_alert_threshold():
        email_threshold_exceeded_alert()
        last_sent_count = last_sent_count + 1
    else:
        logging.warning("Not sending alerts: Sent count and sent time thresholds are exceeded. ")

logging.basicConfig(format='%(asctime)s -- %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=config.get_landmine_log_path(),
                    level=logging.DEBUG)

f = subprocess.Popen(['tail', '-F', '-n', '0', config.get_snort_log_path()],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# TODO: On start, read network interface settings and build snort rule set, then restart snort
while True:
    alert_text = ""
    line = f.stdout.readline().decode("utf-8")
    while line != "\n":
        alert_text = alert_text + line;
        line = f.stdout.readline().decode("utf-8")

    logging.debug("Found snort alert:\n%s\n" % (alert_text))
    process_alert(alert_text)
