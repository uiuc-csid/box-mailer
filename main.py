import csv
from smtplib import SMTP
from email.message import EmailMessage

from boxsdk import Client, OAuth2, DevelopmentClient, BoxAPIException
import click

class PooledSMTP():
    def __init__(self, hostname, max_messages=95):
        self.hostname = hostname
        self.message_count = 0
        self.max_messages = max_messages
        self.connection = None

    def __enter__(self):
        self.connection = SMTP(self.hostname)
        return self

    def __exit__(self, *exc_details):
        self.connection.quit()

    def reconnect(self):
        self.connection.quit()
        self.connection.connect(self.hostname)

    def send_message(self, *args, **kwargs):
        if self.message_count > self.max_messages:
            self.reconnect()
        self.connection.send_message(*args, **kwargs)
        self.message_count += 1


@click.command()
@click.option('--dev-token', envvar='BOXMAILER_DEV_TOKEN')
@click.option('--user-details-file', type=click.File(), default="input.csv")
@click.argument('folder-name')
def main(dev_token, user_details_file, folder_name):
    if dev_token is None:
        client = DevelopmentClient()
    else:
        auth = OAuth2(
            client_id='',
            client_secret='',
            access_token=dev_token,
        )
        client = Client(auth)

    reader = csv.DictReader(user_details_file)
    users_detail = list(reader)

    folder = client.search().query(folder_name, limit=1, result_type='folder').next()
    for user in users_detail:
        item = client.search().query(user['file'], limit=1, ancestor_folders=[folder], result_type='file').next()
        try:
            item.collaborate_with_login(user['login'], role='viewer')
        except BoxAPIException as ex:
            if not ex.code == 'user_already_collaborator':
                raise ex
        user['link'] = item.get_shared_link('collaborators')
    
    # Need collection pooling/limiting due to rate limits
    with PooledSMTP('outbound-relays.techservices.illinois.edu') as sender:
        for user in users_detail:
            message = EmailMessage()
            message['From'] = 'asplund3@illinois.edu'
            message['To'] = user['login']
            message['Subject'] = 'Test files'
            message.set_content(f"Your link to the test file is {user['link']}.")
            sender.send_message(message)

    return

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
