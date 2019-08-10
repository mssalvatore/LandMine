#!/usr/bin/env python3

TEXT="text"
TITLE="title"
BACKTITLE="backtitle"
CHOICES="choices"
FIELDS="fields"

LANDMINE_TITLE = "LandMine Settings"
NETWORK_TITLE = "Network Interfaces"
EMAIL_TITLE = "E-Mail Alert Settings"
SMTP_TITLE = "SMTP Settings"
LOGGING_TITLE = "Logging Settings"
RECIPIENTS_TITLE = "E-Mail Alert Recipients"

EMAIL_MENU = "E-Mail"
LOGGING_MENU = "Logging"
NETWORK_MENU = NETWORK_TITLE
SMTP_MENU = "SMTP"
RECIPIENTS_MENU = "Recipients"
VIEW_ALERT_RECIPIENTS_MENU = "View"
ADD_ALERT_RECIPIENTS_MENU = "Add"
DELETE_ALERT_RECIPIENTS_MENU = "Delete"

TOP_BACKTITLE = LANDMINE_TITLE
NETWORK_BACKTITLE = TOP_BACKTITLE + " - " + NETWORK_MENU
EMAIL_BACKTITLE = TOP_BACKTITLE + " - " + EMAIL_MENU
SMTP_BACKTITLE = EMAIL_BACKTITLE + " - " + SMTP_MENU
SMTP_PASSWORD_BACKTITLE = SMTP_BACKTITLE + " - " + "Password"
LOGGING_BACKTITLE = TOP_BACKTITLE + " - " + LOGGING_MENU
RECIPIENTS_BACKTITLE = EMAIL_BACKTITLE + " - " + RECIPIENTS_MENU

main_menu_text = "What yould you like to configure?"
main_menu_title = LANDMINE_TITLE
main_menu_backtitle = TOP_BACKTITLE
main_menu_choices = [
    ("Network Interfaces", "Choose which network interfaces will be monitored"),
    ("E-Mail", "E-Mail alert settings"),
    ("Logging", "Options pertaining to logging")
]

network_menu_text = "Choose which interfaces to monitor:"
network_menu_title = NETWORK_TITLE
network_menu_backtitle = NETWORK_BACKTITLE

email_menu_text = "Configure e-mail settings"
email_menu_title = EMAIL_TITLE
email_menu_backtitle = EMAIL_BACKTITLE
email_menu_choices = [
    (SMTP_MENU, "Configure outgoing SMTP server and credentials"),
    (RECIPIENTS_MENU, "Configure alert recipients")
]

smtp_menu_text = "SMTP server settings"
smtp_menu_title = SMTP_TITLE
smtp_menu_backtitle = SMTP_BACKTITLE
smtp_menu_fields = [
    ("Host", 1, 1, "smtp.gmail.com", 1, 20, 50, 250, 0x00),
    ("Port", 2, 1, "587", 2, 20, 6, 5, 0x00),
    ("Username", 3, 1, "", 3, 20, 50, 250, 0x00)
]

ENTER_SMTP_PASSWORD = "Enter the password for the user '%s' on the SMTP server '%s'" 
CONFIRM_SMTP_PASSWORD = "Confirm the password for the user '%s' on the SMTP server '%s'" 
smtp_password_title = "SMTP Password"
smtp_password_backtitle = SMTP_PASSWORD_BACKTITLE

logging_input_text = "Location of LandMine log file:"
logging_input_init = "/var/snap/current/common/landmine.log"
logging_input_title = LOGGING_TITLE
logging_input_backtitle = LOGGING_BACKTITLE

recipients_menu_text = "Configure alert recipients"
recipients_menu_title = RECIPIENTS_TITLE
recipients_menu_backtitle = RECIPIENTS_BACKTITLE
recipients_menu_choices = [
    (VIEW_ALERT_RECIPIENTS_MENU, "View alert recipients"),
    (ADD_ALERT_RECIPIENTS_MENU, "Add alert recipients"),
    (DELETE_ALERT_RECIPIENTS_MENU, "Delete alert recipients"),
]
