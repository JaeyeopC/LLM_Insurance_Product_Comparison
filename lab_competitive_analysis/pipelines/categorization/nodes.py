"""
This is a boilerplate pipeline 'categorization'
generated using Kedro 0.19.10
"""

import os 
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import ChatPromptTemplate #, PromptTemplate 
from langchain_core.output_parsers import PydanticOutputParser
import pandas as pd 
from pathlib import Path

class check_product_model(BaseModel):
    is_product: str = Field(description="determine if the content is related to a insurance product")

class classify_category_model(BaseModel):
    category: str = Field(description="determine the category of the insurance product",
                          enum = [                             
                             "Term Life Insurance", "Whole Life Insurance", "Pension Insurance", "Disability Insurance", 
                             "Long-Term Care Pension Insurance", "Health Insurance", "Critical Illness Insurance", "Basic Ability Insurance", 
                             "Long-Term Care Cost Insurance", "Long-Term Care Daily Allowance Insurance", "Liability Insurance", 
                             "Business Interruption Insurance", "Home Contents Insurance", "Building Insurance", "Business Property Insurance", 
                             "Commercial Insurance", "Loan Repayment Insurance", "Construction Performance Insurance", 
                             "Machinery Breakdown and Machinery Insurance", "Credit Insurance", "Fidelity Guarantee Insurance", "Erection Insurance", 
                             "Natural Disaster Insurance", "Accident Insurance", "Travel Insurance", "Transport Insurance", "Private Unemployment Insurance", 
                             "Pet Insurance", "Driver Protection Insurance", "Legal Protection Insurance"]
    )
    keywords: list = Field(..., description="key features extracted from the content") # tagging keywords for the product


def check_product(model_options: dict, check_sys_prompt: str, check_human_prompt: str, data: pd.DataFrame):
    llm = get_model(model_options)
    parser = PydanticOutputParser(pydantic_object=check_product_model)
    format_instructions = parser.get_format_instructions()
    check_product_prompt = ChatPromptTemplate.from_messages([
        ("system", check_sys_prompt),
        ("human", check_human_prompt)
    ]) 

    check_product_chain = check_product_prompt | llm | parser

    is_product_list = []
    for _, row in data.iterrows():
        response = check_product_chain.invoke({
            "company": row["company"],
            "title": row["title"],
            "content": row["content"],
            "format_instructions": format_instructions
            })
        if response.is_product == "yes":
            is_product_list.append(response.is_product)
    data['is_product'] = is_product_list
    data = data[data['is_product'] == "yes"].reset_index(drop=True)
    return data

def save_category_data(model_options: dict, classify_sys_prompt: str, classify_human_prompt: str, processed_crawled_data: pd.DataFrame):
    llm = get_model(model_options) 
    parser = PydanticOutputParser(pydantic_object=classify_category_model)
    format_instructions = parser.get_format_instructions()
    
    classify_product_prompt = ChatPromptTemplate.from_messages([
        ("system", classify_sys_prompt),
        ("human", classify_human_prompt)
    ])

    classify_product_chain = classify_product_prompt | llm | parser

    for idx, row in processed_crawled_data.iterrows():
        response = classify_product_chain.invoke({
            "company": row["company"],
            "title": row["title"],
            "content": row["content"],
            "format_instructions": format_instructions
        })
        processed_crawled_data.at[idx, 'category'] = response.category
        processed_crawled_data.at[idx, 'keywords'] = ",".join(response.keywords)
    
    category_data = processed_crawled_data
    return category_data


# save the current category data as ground truth set, which should be manually corrected.
# The ground truth set will be fixed once we have popluated the table with enough data.
def save_ground_truth_set(category_data: pd.DataFrame):
    category_ground_truth_set = category_data
    return category_ground_truth_set


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
    


