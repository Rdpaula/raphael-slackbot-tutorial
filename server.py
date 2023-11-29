import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime as dt

from flask import Flask, request, make_response, Response

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

from slashCommand import Slash

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

  # send user a response via DM
  # im_id = slack_client.im_open(user=info["user_id"])["channel"]["id"]
  # ownerMsg = slack_client.chat_postMessage(
  #   channel=im_id,
  #   text=commander.getMessage()
  # )

  # # send channel a response
  # response = slack_client.chat_postMessage(
  #   channel='#{}'.format(info["channel_name"]), 
  #   text=commander.getMessage()
  # )

@app.route("/slack/test", methods=["POST"])
def command():
  if not verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)
  info = request.form

  try:
    response = slack_client.chat_postMessage(
      channel=info["channel_id"].format(info["channel_name"]),
      blocks=[
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Clock-bot",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*When:*\nAug 10 - Aug 13"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": True,
						"text": "Start"
					},
					"style": "primary",
					"value": "Start",
          "action_id": "Start"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": True,
						"text": "Stop"
					},
					"style": "danger",
					"value": "click_me_123",
          "action_id": "Stop"
				}
			]
		}
	]
    ).get()
  except SlackApiError as e:
    logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
    logging.error(e.response)
    return make_response("", e.response.status_code)

  return make_response("", response.status_code)

@app.route('/slack/events', methods=['POST'])
def handle_event():

    payload = json.loads(request.form.get('payload'))
    print(payload)
    if payload['type'] == 'block_actions':
        action = payload['actions'][0]['action_id']
        response_url = payload['response_url']  # Use this URL to send additional messages
        
        global before
        if action == 'Start':
            before = dt.now()
            print(before.strftime("%d/%m/%Y %H:%M:%S"))
        elif action == 'Stop':
            # Delete the original message using response_url
            
            try:
              duration = dt.now() - before
              duration = duration.total_seconds()
              hours, remainder = divmod(duration, 3600)
              minutes, seconds = divmod(remainder, 60)
              response = slack_client.chat_update(
              channel=payload['channel']['id'].format(payload["channel"]["id"]), text='{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)), ts=payload["message"]["ts"])#.get()
            except SlackApiError as e:
              logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
              logging.error(e.response)
              return make_response("", e.response.status_code)
    # Send acknowledgment response
    return '', 200

# Start the Flask server
if __name__ == "__main__":
  load_dotenv()
  SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
  SLACK_SIGNATURE = os.environ['SLACK_SIGNATURE']
  slack_client = WebClient(SLACK_BOT_TOKEN)
  verifier = SignatureVerifier(SLACK_SIGNATURE)

  commander = Slash("Hey there! It works.")
  before = dt.now()
  app.run()