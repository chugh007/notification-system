from abc import ABC, abstractmethod
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import smtplib, ssl
import sys
sys.path.append(".")
from library import *
import re

setup_logging()

class PostMessage(ABC):

    def __init__(self):
        pass

    def load_env_vars(self):
        pass

    @abstractmethod
    def sendMessage(self,email,message):
        pass

class Slack(PostMessage):

    def __init__(self):
        super()
        self.load_env_vars()
        self.client = WebClient(token=self.slack_bot_token)

    def load_env_vars(self):
        self.slack_bot_token = os.environ['SLACK_BOT_TOKEN']


    def sendMessage(self,email , message):
        if re.match(r"^@.*",email): #check if entered email is a channel name
            user_id = email[1:] #remove @ and send message to channel
        else:
            resp = self.client.users_lookupByEmail(email = email)  
            user_id = resp.data['user']['id']
        resp = self.client.chat_postMessage(channel=user_id, text= message)
        logging.info("Message {} send to user with email {}" .format(message , email))


class Email(PostMessage):

    def __init__(self):
        super()
        self.load_env_vars()
        self.server = smtplib.SMTP(self.smtp_server,self.smtp_port)
        self.server.ehlo()
        self.server.starttls()


    def load_env_vars(self):
        self.smtp_server = os.environ['SMTP_SERVER']
        self.smtp_port = os.environ.get('SMTP_PORT',587)
        self.service_email = os.environ['SERVICE_EMAIL']
        self.service_password = os.environ['SERVICE_PASSWORD']

    def sendMessage(self,email , message):
        subject = 'Script Alert'
        to = email
        self.server.login(self.service_email, self.service_password)
        headers = "\r\n".join(["from:" + self.service_email,
                        "subject:" + subject,
                        "to:" + email,
                        "MIME-Version: 1.0",
                        "content-type: text/html"])
        content =  headers + "\n\n" + message
        self.server.sendmail(self.service_email, email, content)