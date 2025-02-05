import json
from typing import List
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
import os
from pydantic import BaseModel


def setup_openai_api_key(parameters):
    """
    Set the OpenAI API key and return the initialized ChatOpenAI model.
    """
    os.environ["OPENAI_API_KEY"] = parameters["OPENAI_API_KEY"]["key"]
    return ChatOpenAI(model_name='gpt-4', temperature=0)


class Feature(BaseModel):
    feature_name: str
    feature_questions: List[str]

class InsuranceProduct(BaseModel):
    product_name: str
    features: List[Feature]


def generate_reference_products(parameters) -> List[str]:
    """
    Generate a list of insurance products using the LLM.
    """
    llm = setup_openai_api_key(parameters)

    product_list_prompt = """
As an expert in the German insurance industry, please provide a list of the 20 most common insurance products or policies in Germany. 
The list should be in English and include both mandatory and optional insurances across various categories such as health, vehicle, property, 
liability, life, and others.

Important Instructions:
- Provide the list as a numbered list from 1 to 20.
- Do not include any additional text or explanations.
- Each item should be the name of the insurance product.

List:
"""
    response = llm.predict(product_list_prompt.strip())
    product_names = [
        line.split(". ", 1)[1].strip() for line in response.strip().split("\n") if ". " in line
    ]
    return product_names

def generate_product_features(product_name: str, parameters) -> List[str]:
    """
    Generate a list of features for a given insurance product using the LLM.
    """
    llm = setup_openai_api_key(parameters)

    feature_prompt = f"""
As an expert in the German insurance industry, please provide the 10 most common feature names (max 4 words) of the insurance product "{product_name}". 
The features should be in English, concise, and relevant to the product as offered in Germany.

Important Instructions:
- Provide the features as a numbered list from 1 to 10.
- Each feature name should be a maximum of 4 words.
- Do not include any additional text or explanations.
- Each item should be the name of a key feature.

Features:
"""
    response = llm.predict(feature_prompt.strip())
    feature_names = [
        line.split(". ", 1)[1].strip() for line in response.strip().split("\n") if ". " in line
    ]
    return feature_names

def generate_feature_questions(product_name: str, feature_name: str, parameters) -> List[str]:
    """
    Generate a list of questions for a given feature of an insurance product using the LLM.
    """
    llm = setup_openai_api_key(parameters)

    question_prompt = f"""
For the insurance product "{product_name}" and feature "{feature_name}", please create 2-4 questions that can be used to extract 
the most important details about this feature from text. The questions should be in English, concise, and relevant to the feature and product.

Important Instructions:
- Provide the questions as a numbered list.
- Do not include any additional text or explanations.
- Each question should be clear and focus on extracting key information about the feature.

Questions:
"""
    response = llm.predict(question_prompt.strip())
    questions = [
        line.split(". ", 1)[1].strip() for line in response.strip().split("\n") if ". " in line
    ]
    return questions


def process_reference_data(product_names: List[str], parameters) -> str:
    """
    Process all insurance products, generate features and questions, and return a JSON string.
    """
    insurance_products = []
    for product_name in tqdm(product_names):
        features = []
        feature_names = generate_product_features(product_name, parameters)
        for feature_name in feature_names:
            feature_questions = generate_feature_questions(product_name, feature_name, parameters)
            feature = Feature(
                feature_name=feature_name,
                feature_questions=feature_questions
            )
            features.append(feature)
        insurance_product = InsuranceProduct(
            product_name=product_name,
            features=features
        )
        insurance_products.append(insurance_product.dict())  # Convert Pydantic model to dictionary

    # Convert list of dictionaries to JSON string
    return json.dumps(insurance_products, indent=2, ensure_ascii=False)

