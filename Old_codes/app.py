import os
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

from langchain.chains.summarize import load_summarize_chain
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import json
from autogen import config_list_from_json
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen import UserProxyAgent
import autogen


load_dotenv()
brwoserless_api_key = os.getenv("BROWSERLESS_API_KEY")
serp_api_key = os.getenv("SERP_API_KEY")
config_list = config_list_from_json("OAI_CONFIG_LIST")


# ------------------ Create functions ------------------ #

# Function for google search
def google_search(search_keyword):    
    url = "https://serpapi.com/search"

    payload = json.dumps({
        "q": search_keyword
    })

    headers = {
        'X-API-KEY': serp_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print("RESPONSE:", response.text)
    return response.text

# Function for scraping
def summary(objective, content):
    llm = ChatOpenAI(temperature = 0, model = "gpt-3.5-turbo-16k-0613")

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size = 10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])
    
    map_prompt = """
    Write a summary of the following text for {objective}:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text", "objective"])
    
    summary_chain = load_summarize_chain(
        llm=llm, 
        chain_type='map_reduce',
        map_prompt = map_prompt_template,
        combine_prompt = map_prompt_template,
        verbose = False
    )

    output = summary_chain.run(input_documents=docs, objective=objective)

    return output

def web_scraping(objective: str, url: str):
    #scrape website, and also will summarize the content based on objective if the content is too large
    #objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    print("Scraping website...")
    # Define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url        
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    response = requests.post(f"https://chrome.browserless.io/content?token={brwoserless_api_key}", headers=headers, data=data_json)
    
    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENTTTTTT:", text)
        if len(text) > 10000:
            output = summary(objective,text)
            return output
        else:
            return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")        


# Function for get airtable records
def get_airtable_records(base_id, table_id):
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"

    headers = {
        'Authorization': f'Bearer {airtable_api_key}',
    }

    response = requests.request("GET", url, headers=headers)
    data = response.json()
    print(data)
    return data


# Function for update airtable records

def update_single_airtable_record(base_id, table_id, id, fields):
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"

    headers = {
        'Authorization': f'Bearer {airtable_api_key}',
        "Content-Type": "application/json"
    }

    data = {
        "records": [{
            "id": id,
            "fields": fields
        }]
    }

    response = requests.patch(url, headers=headers, data=json.dumps(data))
    data = response.json()
    return data


# ------------------ Create agent ------------------ #

# Create user proxy agent
user_proxy = UserProxyAgent(name="user_proxy",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=1
    )

# Create researcher agent
research_agent = GPTAssistantAgent(
    name = "Research agent",
    llm_config = {
        "config_list": config_list,
        "assistant_id": "asst_DXSZG3N0doWpLNBGSbpNIG6W"
    }
)

research_agent.register_function(
    function_map={
        "web_scraping": web_scraping,
        "google_search": google_search
    }
)


# Create research manager agent
research_manager = GPTAssistantAgent(
    name="Research manager",
    llm_config = {
        "config_list": config_list,
        "assistant_id": "asst_gBKUfZjK2h4rHHF4JPKMJsAm"
    }
)

# Create researcher writer
research_writer = GPTAssistantAgent(
    name = "Research writer",
    llm_config = {
        "config_list": config_list,
        "assistant_id": "asst_DXSZG3N0doWpLNBGSbpNIG6W"
    }
)

research_writer.register_function(
    function_map={
        "summary": summary
    }
)


# Create group chat
groupchat = autogen.GroupChat(agents=[user_proxy, research_agent, research_manager, research_writer], messages=[], max_round=15)
group_chat_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})


# ------------------ start conversation ------------------ #
message = """
Research the current diagnostic procedure for adult attention deficit hyperactive disorder
"""
user_proxy.initiate_chat(group_chat_manager, message=message)