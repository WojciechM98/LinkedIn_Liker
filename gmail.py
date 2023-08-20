import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup
from executive import LinkHandling
import re


def find_keys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_keys(j, kv):
                yield x


class GmailBot:
    def __init__(self):
        # If modifying scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        self.links = []
        self.creds = None

    def credentials(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def search_for_link(self, max_results_search, msg_title):
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            # Request list of first 10 unread emails
            result = service.users().messages().list(userId='me', maxResults=max_results_search,
                                                     labelIds=['INBOX'], q="is:unread").execute()
            messages = result.get('messages', [])
            if not messages:
                print('You have no unread messages')
            else:
                for message in messages:
                    msg_id = message['id']
                    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                    title = msg['payload']['headers'][3]['value'].lower()
                    # Looking for given title in messages
                    found = title.find(msg_title.lower())
                    if found != -1:
                        print("Email found!")
                        data = list(find_keys(msg, 'data'))[-1]
                        # Decoding encoded data from message
                        decoded_msg = base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4))
                        message = decoded_msg.decode('utf-8')
                        # Using BeautifulSoup to search in decoded message for LinkedIn link
                        soup = BeautifulSoup(message, 'html.parser')
                        try:
                            link = soup.select("a[href*=linkedin]")[0].get("href")
                            self.links.append({"id": msg["id"], "link": link})
                        except IndexError:
                            print(f"LinkedIn link not found.")
                    else:
                        print("Email not found.")

                if not self.links:
                    print("Links not found, attempt abandoned.")
                else:
                    # If links were found proceed with liking post on LinkedIn
                    print(self.links)
                    bot = LinkHandling(self.links)
                    to_remove = bot.login_to_linkedin()
                    for ids in to_remove:
                        service.users().messages().modify(userId='me', id=ids,
                                                          body={"removeLabelIds": ["UNREAD"]}).execute()

        except HttpError as error:
            print(f'An error occurred: {error}')

    def search_for_verification(self, max_results_search):
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            # Request list of unread emails
            result = service.users().messages().list(userId='me', maxResults=max_results_search,
                                                     labelIds=['INBOX'], q="is:unread").execute()
            messages = result.get('messages', [])
            if not messages:
                print('You have no unread messages')
            else:
                for message in messages:
                    msg_id = message['id']
                    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                    # Searching for string containing numbers with length of 6
                    for header in msg['payload']['headers']:
                        if header['name'] == 'Subject':
                            try:
                                ver_code = re.findall(r'\b\d+\b', header['value'])[0]
                                if len(ver_code) == 6:
                                    print("Verification key found!")
                                    return ver_code
                            except IndexError:
                                print(f"Verification key not found.")

        except HttpError as error:
            print(f'An error occurred: {error}')
