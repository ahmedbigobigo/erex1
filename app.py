import os
import json
import requests
import openai
from flask import Flask, request

# Configure OpenAI API key
openai.api_key = "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"

# Configure Facebook Page access token and verify token
PAGE_ACCESS_TOKEN = "EABXQvM1lkVcBAHuOytrLZAgpNn2GW8cZBMw1PWww1JJQcdUfIEbr0RzPZCommZBMho1hA5m4OKFa1ShnNpiXcZBBNQDcqZBXyMZCMxP9lKYN01bqYlTC047mYiWJfX6znS33YbJ9eT7RLOhNoPDRZBmhsKRpMNw4KwtAftPZApGnA7V25qviFc4pHADnPN5oDqyQoRiC2AB5UwwZDZD"
VERIFY_TOKEN = "1234567"

# Set up Flask app
app = Flask(__name__)

# Function to send a message via the Facebook Graph API
def send_message(recipient_id, message):
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
    }
    url = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

# Function to get response from OpenAI API
def get_openai_response(user_message):
    prompt = f"User: {user_message}\nBot:"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = response.choices[0].text.strip()
    return message

# Endpoint for Facebook webhook verification
@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        print("Webhook verified")
        return request.args.get("hub.challenge")
    else:
        print("Invalid webhook verification token")
        return "Invalid verification token"

# Endpoint for receiving incoming messages from Facebook
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"]["text"]
                    bot_message = get_openai_response(user_message)
                    send_message(sender_id, bot_message)
    return "OK"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)