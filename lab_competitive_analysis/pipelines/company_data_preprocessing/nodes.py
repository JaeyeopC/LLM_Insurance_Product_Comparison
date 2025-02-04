"""
This is a boilerplate pipeline 'company_data_preprocessing'
generated using Kedro 0.19.10
"""
import requests
import re
import pandas as pd 
import os 
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import AsyncHtmlLoader # AsyncChromiumLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
# from langchain.text_splitter import RecursiveCharacterTextSplitter


def crawl_comapany_urls(parameters: dict) -> dict: 
    companies = parameters["companies_urls"]
    max_pages = parameters["search_depth"]

    company_urls = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }

    for company in companies:
        company_name = company['name'].lower().replace(' ', '_')
        company_urls[company_name] = [] # Initialize empty list for each company
        
        start_url = company['url']
        visited_urls = set()
        to_visit = [start_url]
        pages_crawled = 0
        
        try:
            print(f'collecting urls for {company_name} with {max_pages} pages')
            while to_visit and pages_crawled < max_pages:
                current_url = to_visit.pop()
                
                if current_url in visited_urls:
                    continue
                    
                visited_urls.add(current_url)
                pages_crawled += 1
                
                response = requests.get(current_url, headers=headers)
                if response.status_code == 200:
                    # Parse HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract and process URLs
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href:
                            # Convert relative URLs to absolute URLs
                            if not href.startswith(('http://', 'https://')):
                                href = urljoin(current_url, href)
                            
                            # Only include URLs from the same domain
                            if urlparse(href).netloc == urlparse(current_url).netloc:
                                if href not in visited_urls:
                                    to_visit.append(href)
                else:
                    print(f'Failed to retrieve the document for {current_url}: Status code {response.status_code}')        
        except Exception as e:
            print(f'Error processing {company_name}: {str(e)}')

        company_urls[company_name] = visited_urls
        print(f'...finished collecting urls for {company_name}')
    print('......finished collecting urls for all companies')

    unprocessed_crawled_data = company_urls
    return unprocessed_crawled_data 

def save_processed_company_data(unprocessed_crawled_data: dict):
    processed_crawled_data = process_crawled_companies_data(unprocessed_crawled_data)

    # Create lists to store the data
    companies = []
    sources = []
    titles = []
    contents = []

    # Extract data from company_data_list
    for company_name, documents in processed_crawled_data.items():
        for doc in documents:
            companies.append(company_name)
            sources.append(doc.metadata.get('source', 'N/A'))
            titles.append(doc.metadata.get('title', 'N/A'))
            contents.append(doc.page_content)

    processed_crawled_data = pd.DataFrame({
        'company': companies, 
        'source': sources,
        'title': titles,
        'content': contents
    })
    return processed_crawled_data 


def process_crawled_companies_data(unprocessed_crawled_data):
    for company_name, visited_urls in unprocessed_crawled_data.items():
        print(f'processing {company_name} with {len(visited_urls)} pages')
        documents = load_html_data(visited_urls)
        documents = html2text_transform(documents)
        documents = clean_special_characters(documents)
        unprocessed_crawled_data[company_name] = documents
        print(f'...finished processing {company_name}')
        processed_crawled_data = unprocessed_crawled_data
    return processed_crawled_data


# get raw html data with meta data  
def load_html_data(visited_urls):
    print('...loading html data')
    loader = AsyncHtmlLoader(list(visited_urls))
    return loader.load() 


# convert html to plain text
def html2text_transform(documents):
    print(f'...converting html to plain text')
    html2text = Html2TextTransformer()
    return html2text.transform_documents(documents)

def clean_special_characters(documents):
    print(f'...cleaning special characters')
    return [Document(page_content=re.sub(r'[\n\r\t#*_`>-]', '', doc.page_content), metadata=doc.metadata) for doc in documents]

# def summarize_documents(documents, model_options: dict):
#     print(f'...summarizing documents')
#     llm = get_model(model_options)
    
#     prompt = ChatPromptTemplate.from_messages([
#             ("system", "erase the unnecessary sentences and characters from the following webpage, while keeping the original content: \n\n [context]{context}[context]")
#         ])
#     # summary_chain = create_stuff_documents_chain(llm, prompt)
#     chain = prompt | llm 
#     return [Document(page_content=chain.invoke({"context": documents}).content, metadata=doc.metadata) for doc in documents]
    

def authentication():
    load_dotenv() 
    OpenAI_key = os.getenv("OPENAI_API_KEY")
    if not OpenAI_key:
        raise ValueError("OpenAI API key not found. Please check your authentication key path.") 
    
    
def get_model(model_options: dict):
    authentication() 
    model_name = model_options["model_name"]
    temperature = model_options["temperature"]
    max_tokens = model_options["max_tokens"]

    llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
    return llm