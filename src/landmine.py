#!/usr/bin/env python3

import datetime
import logging
import re
import smtplib
import subprocess
import time

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
    s = smtplib.SMTP(host="", port=587)
    s.starttls()
    s.login("", "")

    from_address = ""
    subject = "Snort Alert!"

    try:
        s.sendmail(from_address, to, message)
    except SMTPException as e:
        logging.error("Caught SMTP exception: %s" % (str(e)))

email_address = ""
sms_email_address = ""
def email_alert(alert_lines):
    logging.info("Sending email with alert details")
    timestamp = parse_timestamp(alert_lines)
    rule_id = parse_rule_id(alert_lines)
    alert_msg = parse_alert_msg(alert_lines)
    protocol = parse_protocol(alert_lines)
    packet_header_info = parse_packet_ip_port_direction(alert_lines)

    message = ("From: \n"
               "To: \n"
               "Subject: LandMine Alert!\n\n"
               " Timestamp: " + timestamp + "\n"
               " Rule ID:" + rule_id + "\n"
               " Message: " + alert_msg + "\n"
               " Protocol: " + protocol + "\n"
               " Packet Data:" + packet_header_info + "\n"
              )

    send_email(email_address, message)
    now = datetime.datetime.now()
    if now.hour >= 9 and now.hour <= 21: # FIX HARD CODED VALUES
        send_email(sms_email_address, message)


def email_threshold_exceeded_alert():
    logging.info("Email threshold exceeded, sending corresponding message.")
    message = ("From: \n"
               "To: \n"
               "Subject: LandMine Alert!\n\n"
               " Email alert threshold exceeded. See /var/log/snort/alert for more info.\n"
              )

    send_email(email_address, message)
    now = datetime.datetime.now()
    if now.hour >= 9 and now.hour <= 21: # FIX HARD CODED VALUES
        send_email(sms_email_address, message)

last_sent_time = 0
last_sent_timeout = 600
last_sent_count = 0
last_sent_count_threshold = 3
def process_alert(alert_text):
    global last_sent_time
    global last_sent_count
    alert_lines = alert_text.split('\n');
    if (time.time() - last_sent_timeout) > last_sent_time:
        last_sent_count = 0

    if last_sent_count < last_sent_count_threshold:
        email_alert(alert_lines)
        last_sent_count = last_sent_count + 1
        last_sent_time = time.time()
    elif last_sent_count == last_sent_count_threshold:
        email_threshold_exceeded_alert()
        last_sent_count = last_sent_count + 1
    else:
        logging.warning("Not sending alerts: Sent count and sent time thresholds are exceeded. ")

logging.basicConfig(format='%(asctime)s -- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/var/log/snort/landmine.log', level=logging.DEBUG)

f = subprocess.Popen(['tail', '-F', '-n', '0', "/var/log/snort/alert"],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
while True:
    alert_text = ""
    line = f.stdout.readline().decode("utf-8")
    while line != "\n":
        alert_text = alert_text + line;
        line = f.stdout.readline().decode("utf-8")

    logging.debug("Found snort alert:\n%s\n" % (alert_text))
    process_alert(alert_text)
