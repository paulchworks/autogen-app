import autogen
from user_proxy_webagent import UserProxyWebAgent
import asyncio
import requests
import json
import os

config_list = [
    {
        "model": "gpt-4o-mini",
    }
]
llm_config_assistant = {
    "model":"gpt-4o-mini",
    "temperature": 0,
    "config_list": config_list,
        "functions": [
        {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    }
                },
                "required": ["query"],
            },
        },
    ],
}
llm_config_proxy = {
    "model":"gpt-4o-mini",
    "temperature": 0,
    "config_list": config_list,
}

#############################################################################################
# this is where you put your Autogen logic, here I have a simple 2 agents with a function call
class AutogenChat():
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config=llm_config_assistant,
            system_message="""You are a helpful assistant, help the user find the status of his order. 
            Only use the tools provided to do the search. Only execute the search after you have all the information needed. 
            When you ask a question, always add the word "Let me know" at the end.
            When you respond with the status add the word Thank You"""
        )
        self.user_proxy = UserProxyWebAgent(  
            name="user_proxy",
            human_input_mode="ALWAYS", 
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("Thank you"),
            code_execution_config=False,
            function_map={
                "web_search": self.web_search
            }
        )

        # add the queues to communicate 
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.assistant,
            clear_history=True,
            message=message
        )

    # Function call 
    def web_search(self, query=None):
        endpoint = os.getenv('BING_ENDPOINT')
        subscription_key = os.getenv('BING_KEY')
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        mkt = 'en-US'
        count = '5'
        freshness = "Week"
        params = { 'q': str(query), 'mkt': mkt , 'count': count, 'freshness': freshness}
        web_search_result = requests.get(endpoint, headers=headers, params=params)
    
        # Check if the request was successful
        if web_search_result.status_code == 200:
            # Convert the JSON response to a string and return it
            return json.dumps(web_search_result.json())
        else:
            # If the request failed, return an error message as a string
            return f"Error: Unable to fetch data. Status code: {web_search_result.status_code}"
