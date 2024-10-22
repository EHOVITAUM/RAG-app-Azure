import os
from openai import AzureOpenAI

# Initialize the Azure OpenAI client with credentials from environment variables
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT')
)

def get_embeddings(text, model="text-embedding-3-large"):
    response = client.embeddings.create(
        input=text,
        model=model
    )
    
    # Extract the embeddings from the response
    embedding = response.data[0].embedding
    
    return embedding, model