import autogen
from user_proxy_webagent import UserProxyWebAgent
import asyncio
import requests
import json
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime

# Get the current date and time
current_datetime = datetime.now()

# Extract the current year
current_year = current_datetime.year

# Format the current date (optional)
current_date = current_datetime.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD

# Load environment variables from .env file
load_dotenv()

llm_client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2024-06-01",
  azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT") 
)

search_client = SearchClient(
    endpoint= os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
    index_name= os.getenv("AZURE_SEARCH_INDEX"),
    key= os.getenv("AZURE_SEARCH_API_KEY"),
    credential=AzureKeyCredential(str(os.getenv("AZURE_SEARCH_API_KEY")))
 )


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
        {
            "name": "document_search",
            "description": "Search the document for information",
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
        }
        
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
            system_message=f"""Your name is PaulchWorks. Today is {current_date} You are a helpful research consultant, 
            help the user find the most accurate answers and analytical intepretation of information. 
            Only use the tools provided to do the search. You must provide titles on the document 
            retrieved. If web search is used, always provide the link of the data sources and you 
            must let the user know which responses are based on web searches. Only execute 
            the search after you have all the information needed. Your chain-of-thoughts should always
            be to first analyse and understand the key issues of the topic. Then, you should
            search and retrieve the most relevant information. Finally and most
            importantly, apply the information found from the two searches, craft a coherent summary of 
            all the information and provide a recommendation as answer. Be as detailed as possible in 
            your responses. When you ask a question, always add the words "Let me know" at the end. 
            When you respond with the status add the words "Thank You" at the end. Remove ### in your responses.
            """
        )
        self.user_proxy = UserProxyWebAgent(  
            name="user_proxy",
            human_input_mode="ALWAYS", 
            max_consecutive_auto_reply=20,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("Thank you"),
            code_execution_config=False,
            function_map={
                "web_search": self.web_search,
                "document_search": self.document_search
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
        count = '10'
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

    def document_search(self, query=None):
        # Step 1: Generate Embeddings
        embeddings = llm_client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        )
        embedding_vector = embeddings.data[0].embedding  # Extract the embedding vector

        # Step 2: Perform Hybrid Search
        search_results = search_client.search(
            search_text=query,  # Full-text search query
            vector_queries=[  # Vector query
                {
                    "kind": "vector",  # Specify the kind of query
                    "vector": embedding_vector,  # Embedding vector
                    "fields": "text_vector",  # Field in the index containing embeddings
                    "k": 10  # Number of nearest neighbors to retrieve
                }
            ],
            select=["title", "chunk"],  # Fields to include in the results
            top=10,  # Maximum number of results to return
            query_type="semantic",  # Enable semantic search
            semantic_configuration_name=os.getenv("AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG")  # Semantic config name
        )

        # Step 3: Process Results
        results = []
        for result in search_results:
            results.append(result)

        return json.dumps(results)
