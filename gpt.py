import os
import openai
from dotenv import load_dotenv, find_dotenv
from prompts import *

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION')

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_API_KEY

def fretish_convert(requirement):
    conversation = [{"role": "system", "content": FRETISH_CONVERT}]
    conversation.append({"role": "user", "content": requirement})

    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=conversation)
    return response['choices'][0]['message']['content']

def inconsistency_check(requirements):
    #TODO: add the inconsistency check prompt
    #TODO: add the requirements to the prompt
    conversation = [{"role": "system", "content": INCONSISTENCY_CHECK}]
    for requirement in requirements:
        conversation.append({"role": "user", "content": requirement})
    
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=conversation)
    return response['choices'][0]['message']['content']

#print openai key
print(OPENAI_API_KEY)