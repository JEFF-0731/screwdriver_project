import os

import requests
import json

class LineBot:
    def __init__(self):
        self.group_id = 'Cc0beef9e1369c28ba39c4d0daff26cc9'
    def send_line(self, word):
        # my_str = "https://api.line.me/v2/bot/message/push"
        # api_key = "Bearer wAZNCiuIZp8sAMLWwYNjrNOQsJfxvcBeGDvRoIFEM8jZT06e+/yhMPOMg5zNea4ZO9ZthyT++U+Hd2+wFQJBL4pt9Os8yBwbNFiuQSCGHUxZtmp6ZPSSPhRQURvO5S0hQPq/W8hY9WdAr+w3JL3nBQdB04t89/1O/w1cDnyilFU="
        #
        # # JSON
        # payload = {
        #     "to": self.group_id,
        #     "messages": [
        #         {
        #             "type": "text",
        #             "text": word
        #         }
        #     ]
        # }
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": api_key
        # }
        #
        # # POST
        # response = requests.post(my_str, headers=headers, json=payload)
        #
        # # Get response information
        # status = response.status_code
        # response_text = response.text
        pass
        return 404
