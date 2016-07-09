import httplib2
import os
import datetime
import argparse

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from flask import Flask
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Signup Form'

TOKEN = 'apasaveslives'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-signup.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        credentials = tools.run_flow(flow, store, flags)
    return credentials


def get_service(credentials):
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Insert(Resource):

    def __init__(self):
        super().__init__()
        self.credentials = get_credentials()
        self.spreadsheet_id = '13G18E8A8Z4x9Utq3Kl55vahODs1eDrhT7Qz7atap1LU'
        service = get_service(self.credentials)
        sheets = service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id).execute()
        self.sheet_id = sheets['sheets'][0]['properties']['sheetId']

    @staticmethod
    def validate():
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('interests', type=str, required=True)
        parser.add_argument('lives_with', type=str, required=True)
        parser.add_argument('lifestyle', type=str, required=True)
        parser.add_argument('fostering', type=str, required=True)
        parser.add_argument('_token', type=str, required=True)
        return parser.parse_args()
        
    def post(self):
        args = self.validate()
        if args['_token'] != TOKEN:
            return {'error': 'unauthorized'}
        self.append_row(args)
        return {}

    def append_row(self, data):
        service = get_service(self.credentials)
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                'requests': [
                    {
                        'appendCells': {
                            'sheetId': self.sheet_id,
                            'rows': [
                                {
                                    'values': [
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=NOW()"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['name']
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['email']
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['interests']
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['lives_with']
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['lifestyle']
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": data['fostering']
                                            }
                                        }
                                    ]
                                }
                            ],
                            'fields': '*'
                        }
                    }
                ]
            }).execute()

        
api.add_resource(HelloWorld, '/')
api.add_resource(Insert, '/insert')


if __name__ == '__main__':
    app.run(debug=True)
