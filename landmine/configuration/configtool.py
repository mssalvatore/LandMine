#!/usr/bin/env python3

from .configuration import Configuration
from dialog import Dialog
from . import dialog_constants as dc
import psutil
import re
from socket import AddressFamily
import sys


config = Configuration()

def loop_dialog(d, dialog_callback, extra_callback=None, cancel_callback=None):
    show_dialog = True
    
    while show_dialog:
        try:
            code, tag = dialog_callback(d)

            if code == d.OK:
                dialog_callbacks[tag](d)
            if code == d.EXTRA:
                if extra_callback is not None:
                    extra_callback(d)
                    #TODO: else raise exception
            if code in (d.CANCEL, d.ESC):
                # TODO: Check for unsaved changes and warn about discarding changes
                if cancel_callback is not None:
                    cancel_callback()
                show_dialog = False
        except Exception as ex:
            show_exception_msg(d, ex)

def show_exception_msg(d, ex):
    d.msgbox("An error occurred while trying to save the configuration:\n\n%s" % str(ex), title="Error", height=10, width=72)
        
def main():
    d = Dialog(autowidgetsize=True)
    loop_dialog(d, main_menu_dialog, save_config)
    # TODO: cancel_callback(): Are you sure you want to overwite the config file?
    # TODO: cancel_callback(): Only save if there are changes, warn otherwise

def main_menu_dialog(d):
    return d.menu(dc.main_menu_text,
                  title=dc.main_menu_title,
                  backtitle=dc.main_menu_backtitle,
                  extra_button=True, extra_label="Save",
                  choices=dc.main_menu_choices)


def show_network_dialog(d):
    d.checklist(dc.network_menu_text,
                title=dc.network_menu_title,
                backtitle=dc.network_menu_backtitle,
                choices=get_network_if_data())

    # TODO: Store choices

def get_network_if_data():
    if_choices = []
    net_ifaces = psutil.net_if_addrs()
    for iface in net_ifaces:
        for address in net_ifaces[iface]:
            if address.family in (AddressFamily.AF_INET, AddressFamily.AF_INET6):
                bare_address = re.sub(r'%.*$', "", address.address)
                if_choices.append((iface, bare_address, False))

    return if_choices

def show_email_dialog(d):
    loop_dialog(d, email_dialog)

def email_dialog(d):
    return d.menu(dc.email_menu_text,
                  title=dc.email_menu_title,
                  backtitle=dc.email_menu_backtitle,
                  choices=dc.email_menu_choices)

def show_smtp_dialog(d):
    loop_dialog(d, smtp_dialog, extra_callback=store_smtp_password)

    #TODO: Validate port
    #TODO: Offer to send test email

def smtp_dialog(d):
    return d.mixedform(dc.smtp_menu_text,
                       dc.smtp_menu_fields,
                       title=dc.smtp_menu_title,
                       backtitle=dc.smtp_menu_backtitle,
                       extra_button=True, extra_label="Set Password", insecure=True)

def store_smtp_password(d):
        password = show_smtp_password_dialog(d, config.smtp_server, config.smtp_username)
        config.smtp_password = password


def show_smtp_password_dialog(d, host, username):
    while True:
        code, password1 = d.passwordbox(dc.ENTER_SMTP_PASSWORD % (username, host),
                                        title=dc.smtp_password_title,
                                        backtitle=dc.smtp_password_backtitle,
                                        insecure=True)

        code, password2 = d.passwordbox(dc.CONFIRM_SMTP_PASSWORD % (username, host),
                                        title=dc.smtp_password_title,
                                        backtitle=dc.smtp_password_backtitle,
                                        insecure=True)

        if password1 != password2:
            d.msgbox("Error: The passwords do not match. Please try again.", height=5, width=72)
        else:
            return password1

def show_recipients_dialog(d):
    loop_dialog(d, recipients_dialog)

def recipients_dialog(d):
    return d.menu(dc.recipients_menu_text,
                  title=dc.recipients_menu_title,
                  backtitle=dc.recipients_menu_backtitle,
                  choices=dc.recipients_menu_choices)

def view_recipients_dialog(d):
    pass

def add_recipients_dialog(d):
    pass

def delete_recipients_dialog(d):
    pass

def show_logging_dialog(d):
    code, user_input = d.inputbox(dc.logging_input_text,
                           init=dc.logging_input_init,
                           backtitle=dc.logging_input_backtitle,
                           title=dc.logging_input_title)

    #TODO: Validate path
    if code == d.OK:
        config.landmine_log_path = user_input

def save_config(d):
    config.save_config()

dialog_callbacks = {dc.NETWORK_MENU: show_network_dialog,
                    dc.EMAIL_MENU: show_email_dialog,
                    dc.LOGGING_MENU: show_logging_dialog,
                    dc.SMTP_MENU: show_smtp_dialog,
                    dc.RECIPIENTS_MENU: show_recipients_dialog,
                    dc.VIEW_ALERT_RECIPIENTS_MENU: view_recipients_dialog,
                    dc.ADD_ALERT_RECIPIENTS_MENU: add_recipients_dialog,
                    dc.DELETE_ALERT_RECIPIENTS_MENU: delete_recipients_dialog,
                    }

