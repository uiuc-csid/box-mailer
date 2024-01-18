#!/usr/bin/env python3

import csv
from string import Template
from smtplib import SMTP
from email.message import EmailMessage

from boxsdk import Client, OAuth2, DevelopmentClient, BoxAPIException
from boxsdk.object.folder import Folder
from boxsdk.object.file import File
import click

email_template = Template("""A new item has been shared with you on Box:

Item: ${file}
Link: ${link}

Please beware of phishing. If you are not sure about the authenticity of this
email, please log in to the Illinois Box site manually instead of following the link.

If you can't log in to Box, you must enable your Illinois Box account on the
Illinois Cloud Dashboard first:
https://cloud-dashboard.illinois.edu""")

# This function cannot be named "send_email" or it will conflict with
# the similarly-named argument for main. (The argument for main is
# auto-named by the click library based on the matching option.)
def send_email_fun(details, connection):
    message = EmailMessage()
    message['From'] = 'no-reply@illinois.edu'
    message['To'] = details['login']
    message['Subject'] = '[Box Mailer] New items shared on Illinois Box'

    message.set_content(email_template.substitute(file=details['file'], link=details['link']))
    connection.send_message(message)

# The auto_envvar_prefix feature may not work correctly for options
# with dashes in the name, but the envvar argument can be given explicitly.

@click.command()
@click.option('--dev-token', envvar='BOXMAILER_DEV_TOKEN', help='Box development token. See README for details')
@click.option('--access-token', envvar='BOXMAILER_ACCESS_TOKEN', help='Box access token. Mutually exclusive with --dev-token.')
@click.option('--user-details-file', type=click.File(), default="input.csv", help='Defaults to input.csv')
@click.option('--dirs/--files', default=True, help='Share folders or files. Defaults to folders')
@click.option('--send-email', type=click.BOOL, default=False, help='Send confirmation emails to students')
@click.option('--folder-id-mode', envvar='BOXMAILER_FOLDER_ID_MODE', is_flag=True, default=False, help='Specify an ID for base_folder instead of a remote path')
@click.option('-v', '--verbose', count=True, help='Verbose output')
@click.argument('base-folder')
def main(dev_token, access_token, user_details_file, dirs, send_email, folder_id_mode, verbose, base_folder):
    if access_token and dev_token:
        raise Exception('Error: access token and dev token are mutually exclusive.')
    if access_token is None:
        access_token = dev_token

    # Get API client
    if access_token is None:
        client = DevelopmentClient()
    else:
        auth = OAuth2(
            client_id='',
            client_secret='',
            access_token=access_token,
        )
        client = Client(auth)

    # Read in list of users
    reader = csv.DictReader(user_details_file)
    # Map items back to users
    users_dict = { user['file'] : user for user in reader }
    processed_items = set()

    # Get reference to base folder
    if folder_id_mode:
        folder = client.folder(folder_id=base_folder).get()
    else:
        folder = client.search().query(base_folder, limit=1, result_type='folder').next()

    if verbose:
        print(f"Got folder: {folder.name}")

    item_type = Folder if dirs else File
    for item in folder.get_items():
        if isinstance(item, item_type) and item.name in users_dict:
            try:
                # Share item with user
                user = users_dict[item.name]
                user['link'] = "(not defined)"
                user['already_collaborator'] = False
                item.collaborate_with_login(user['login'], role='viewer')
            except BoxAPIException as ex:
                # Error if already sharing
                if not ex.code == 'user_already_collaborator':
                    raise ex
                user['already_collaborator'] = True
            try:
                user['link'] = item.get_shared_link(access='collaborators')
            except BoxAPIException as ex:
                # TODO: handle this better for automation and logging
                print('Error: Could not get shared link for item:', item.name)
                raise ex
            processed_items.add(item.name)
        else:
            print('Warning: Item on Box but not listed in input: ' + item.name)

    for item_name, details in users_dict.items():
        if item_name not in processed_items:
            print(
                'Warning: Item in input could not be shared on Box:',
                '"' + item_name + '"',
                'Associated details:',
                str(details)
            )

    if send_email:
        # Send email to each new student
        connection = SMTP('outbound-relays.techservices.illinois.edu')
        messages = 0

        for item_name, details in users_dict.items():
            # Don't send email if processing failed or already sharing
            if item_name not in processed_items:
                if verbose:
                    print('Item could not be processed, so will not email for:', item_name)
                continue
            if 'already_collaborator' not in details or details['already_collaborator']:
                if verbose:
                    print('Already collaborator, so will not email for:', item_name)
                continue

            # Reconnect if we are nearing rate limiting
            if messages >= 95:
                connection.quit()
                connection = SMTP('outbound-relays.techservices.illinois.edu')
                messages = 0

            send_email_fun(details, connection)
            messages += 1

    return

if __name__ == '__main__':
    main(auto_envvar_prefix='BOXMAILER') # pylint: disable=no-value-for-parameter
