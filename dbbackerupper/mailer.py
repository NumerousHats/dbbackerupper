from yagmail import *


def authorize(address):
    yag = SMTP(address, oauth2_file="~/oauth2_creds.json")
