#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),CLIENT_SECRETS_FILE))

YOUTUBE_SCOPES = (
  # This OAuth 2.0 access scope allows for read-only access to the authenticated
  # user's account, but not other types of account access.
  "https://www.googleapis.com/auth/youtube.readonly",
  # This OAuth 2.0 scope grants access to YouTube Content ID API functionality.
  "https://www.googleapis.com/auth/youtubepartner")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_PARTNER_API_SERVICE_NAME = "youtubePartner"
YOUTUBE_PARTNER_API_VERSION = "v1"


# Authorize the request and store authorization credentials.
def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

  youtube_partner = build(YOUTUBE_PARTNER_API_SERVICE_NAME,
    YOUTUBE_PARTNER_API_VERSION, http=credentials.authorize(httplib2.Http()))

  return (youtube, youtube_partner)

def get_content_owner_id(youtube_partner):
  # Call the contentOwners.list method to retrieve the ID of the content
  # owner associated with the currently authenticated user's account. If the
  # authenticated user's has access to multiple YouTube content owner accounts,
  # you need to iterate through the results to find the appropriate one.
  content_owners_list_response = youtube_partner.contentOwners().list(
    fetchMine=True
  ).execute()

  return content_owners_list_response["items"][0]["id"]

def list_managed_channels(youtube, content_owner_id):
  print( "Channels managed by content owner '%s':" % content_owner_id)

  # Retrieve a list of the channels that the content owner manages.
  channels_list_request = youtube.channels().list(
    onBehalfOfContentOwner=content_owner_id,
    managedByMe=True,
    part="snippet",
    maxResults=50
  )

  while channels_list_request:
    channels_list_response = channels_list_request.execute()

    for channel_item in channels_list_response["items"]:
      channel_title = channel_item["snippet"]["title"]
      channel_id = channel_item["id"]
      print( "  %s (%s)" % (channel_title, channel_id))

    channels_list_request = youtube.channels().list_next(
      channels_list_request, channels_list_response)


if __name__ == "__main__":
  args = argparser.parse_args()
  (youtube, youtube_partner) = get_authenticated_services(args)
  content_owner_id = get_content_owner_id(youtube_partner)
  list_managed_channels(youtube, content_owner_id)