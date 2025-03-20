import os
import json
from typing import List
from pydantic import BaseModel
from tqdm import tqdm

# Import LangChain components
from langchain.chat_models import ChatOpenAI

# Ensure your OpenAI API key is set
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("Please set your OpenAI API key as an environment variable named 'OPENAI_API_KEY'.")

# Step 1: Define Pydantic models
class Feature(BaseModel):
    feature_name: str
    feature_questions: List[str]

class InsuranceProduct(BaseModel):
    product_name: str
    features: List[Feature]

# Initialize the LLM
llm = ChatOpenAI(model_name='gpt-4', temperature=0)

# Step 2: Set up prompts
def get_insurance_products():
    # Define the prompt for generating insurance products
    product_list_prompt = """
As an expert in the German insurance industry, please provide a list of the 20 most common insurance products or policies in Germany. The list should be in English and include both mandatory and optional insurances across various categories such as health, vehicle, property, liability, life, and others.

Important Instructions:
- Provide the list as a numbered list from 1 to 20.
- Do not include any additional text or explanations.
- Each item should be the name of the insurance product.

List:
"""

    # Call the LLM directly
    response = llm.predict(product_list_prompt.strip())

    # Parse the response to get the product names
    product_names = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if line:
            # Remove numbering and extract the product name
            if '. ' in line:
                product_name = line.split('. ', 1)[1].strip()
            elif ') ' in line:
                product_name = line.split(') ', 1)[1].strip()
            else:
                product_name = line
            product_names.append(product_name)

    return product_names

def get_product_features(product_name):
    # Define the prompt for generating features
    feature_prompt = f"""
As an expert in the German insurance industry, please provide the 10 most common feature names (max 4 words) of the insurance product "{product_name}". The features should be in English, concise, and relevant to the product as offered in Germany.

Important Instructions:
- Provide the features as a numbered list from 1 to 10.
- Each feature name should be a maximum of 4 words.
- Do not include any additional text or explanations.
- Each item should be the name of a key feature.

Features:
"""

    # Call the LLM directly
    response = llm.predict(feature_prompt.strip())

    # Parse the response to get the features
    feature_names = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if line:
            # Remove numbering and extract the feature name
            if '. ' in line:
                feature_name = line.split('. ', 1)[1].strip()
            elif ') ' in line:
                feature_name = line.split(') ', 1)[1].strip()
            else:
                feature_name = line
            feature_names.append(feature_name)

    return feature_names

def get_feature_questions(feature_name, product_name):
    # Define the prompt for generating feature questions
    question_prompt = f"""
For the insurance product "{product_name}" and feature "{feature_name}", please create 2-4 questions that can be used to extract the most important details about this feature from text. The questions should be in English, concise, and relevant to the feature and product.

Important Instructions:
- Provide the questions as a numbered list.
- Do not include any additional text or explanations.
- Each question should be clear and focus on extracting key information about the feature.

Questions:
"""

    # Call the LLM directly
    response = llm.predict(question_prompt.strip())

    # Parse the response to get the questions
    questions = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if line:
            # Remove numbering and extract the question
            if '. ' in line:
                question = line.split('. ', 1)[1].strip()
            elif ') ' in line:
                question = line.split(') ', 1)[1].strip()
            else:
                question = line
            questions.append(question)

    return questions

def main():
    # Step 3: Generate the list of insurance products
    print("Generating list of insurance products...")
    insurance_products = []
    product_names = get_insurance_products()

    # Step 4: For each product, generate the features and questions
    print("Generating features and questions for each product...")
    for product_name in tqdm(product_names):
        feature_names = get_product_features(product_name)
        features = []
        for feature_name in feature_names:
            feature_questions = get_feature_questions(feature_name, product_name)
            feature = Feature(
                feature_name=feature_name,
                feature_questions=feature_questions
            )
            features.append(feature)
        insurance_product = InsuranceProduct(
            product_name=product_name,
            features=features
        )
        insurance_products.append(insurance_product)

    # Step 5: Output the data to a JSON file
    output_data = [product.dict() for product in insurance_products]

    with open('4_insurance_reference_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("Data saved to insurance_reference_data.json")

if __name__ == "__main__":
    main()
