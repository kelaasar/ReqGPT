import os
import sys

import constants
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator

os.environ["OPENAI_API_KEY"] = constants.APIKEY

query = sys.argv[1]
print(query)

loader = TextLoader('C:/Users/kelz9/OneDrive/Documents/Visual Studio Projects/ReqGPT/openai/data.txt')
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query))