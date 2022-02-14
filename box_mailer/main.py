#!/usr/bin/env python3

import csv
from string import Template
from smtplib import SMTP
from email.message import EmailMessage

from boxsdk import Client, OAuth2, DevelopmentClient, BoxAPIException
from boxsdk.object.folder import Folder
from boxsdk.object.file import File
import click

email_template = Template("""Your link to the test item is ${link}.

If you cant login to Box you must enable your account through the following link
https://cloud-dashboard.illinois.edu""")

def send_email(user, connection):
    message = EmailMessage()
    message['From'] = 'boxmailer@illinois.edu'
    message['To'] = user['login']
    message['Subject'] = 'Test files'

    message.set_content(email_template.substitute(link=user['link']))
    connection.send_message(message)

@click.command()
@click.option('--dev-token', help='Box development token. See README for details')
@click.option('--user-details-file', type=click.File(), default="input.csv", help='Defaults to input.csv')
@click.option('--dirs/--files', default=True, help='Share folders or files. Defaults to folders')
@click.option('--send-email', type=click.BOOL, default=False, help='Send confirmation emails to students')
@click.argument('base-folder')
def main(dev_token, user_details_file, dirs, send_email, base_folder):
    # Get API client
    if dev_token is None:
        client = DevelopmentClient()
    else:
        auth = OAuth2(
            client_id='',
            client_secret='',
            access_token=dev_token,
        )
        client = Client(auth)

    # Read in list of users
    reader = csv.DictReader(user_details_file)
    users_dict = { user.file : user for user in reader }

    # Get reference to base folder
    folder = client.search().query(base_folder, limit=1, result_type='folder').next()

    item_type = Folder if dirs else File
    for item in folder.get_items():
        if isinstance(item, item_type) and item.name in users_dict:
            try:
                # Share item with user
                user = users_dict[item.name]
                item.collaborate_with_login(user['login'], role='viewer')
                user['link'] = item.get_shared_link('collaborators')
            except BoxAPIException as ex:
                # Error if already sharing
                if not ex.code == 'user_already_collaborator':
                    raise ex
    
    if send_email:
        # Send email to each new student
        connection = SMTP('outbound-relays.techservices.illinois.edu')
        messages = 0

        for user, details in users_dict.items():
            # Don't send email if already sharing
            if 'link' not in user:
                continue

            # Reconnect if we are nearing rate limiting
            if messages >= 95:
                connection.quit()
                connection = SMTP('outbound-relays.techservices.illinois.edu')

            send_email(user, connection)
            messages += 1

    return

if __name__ == '__main__':
    main(auto_envvar_prefix='BOXMAILER') # pylint: disable=no-value-for-parameter
