"""
This is a boilerplate pipeline 'poster_comparison'
generated using Kedro 0.19.10
"""

import os
from dotenv import load_dotenv
import pandas as pd  # Import pandas to fix the error
from langchain.chat_models import ChatOpenAI
import json
from langchain.prompts import PromptTemplate
import pandas as pd


def convert_json_to_csv(classification_json_data_dir: str):
    # Initialize an empty list to store all products
    all_products = []

    print(os.listdir(classification_json_data_dir))
    # # Iterate over each JSON file in the directory
    for product_file in os.listdir(classification_json_data_dir):
        print(f"...reading {product_file}")
        if product_file.endswith(".json"):
            with open(os.path.join(classification_json_data_dir, product_file), 'r', encoding='utf-8') as file:
                product_data = json.load(file)

                company_name = product_file.split("_")[0]  # Change to match the company name from file names 
                for product in product_data.values(): 
                    product_name = product["product_name"]
                    category = product["category"]
                    details = "\n".join(product["details"])
                
                    all_products.append({
                        "company_name": company_name,
                        "product_name": product_name,
                        "category": category,
                        "details": details
                    })

    print(f"json files saved to csv")
    print("="*100)
    # Create a single DataFrame for all products
    all_products_df = pd.DataFrame(all_products)
    return all_products_df


def compare_products(all_products_df, comparison_prompt, predefined_category_list, model_options):
    authentication()
    chat_model = get_model(model_options)
    prompt = comparison_prompt

    company_names = all_products_df["company_name"].unique()
    company_names_n = len(company_names)
    
    # Initialize a list to store the data for the DataFrame
    comparison_data = []

    # Iterate over all company names and get all rows for each pair of company names
    for i in range(0, company_names_n):
        if i+1 < company_names_n:
            company_1 = company_names[i]
            company_2 = company_names[i+1]
        else:
            break

        # Get rows for company_1 and company_2
        company_1_rows = all_products_df[all_products_df['company_name'] == company_1]
        company_2_rows = all_products_df[all_products_df['company_name'] == company_2]

        # Find common categories
        common_categories = list(set(company_1_rows['category']).intersection(set(company_2_rows['category'])))

        for j, category in enumerate(common_categories[:5]):
            print(f"categories: {j+1}/{len(common_categories)} | comparing {company_1.capitalize()} & {company_2.capitalize()} | category: {category}" )
            if category not in predefined_category_list:
                print(f"category {category} is not in both companies")
                break
            company_1_category_products = company_1_rows[company_1_rows['category'] == category]
            company_2_category_products = company_2_rows[company_2_rows['category'] == category]

            # one category can contain several products 
            company_1_product_info_list = company_1_category_products.apply(lambda row: f"Product Name: {row['product_name']}\nDetails: {row['details']}", axis=1).to_list()
            company_2_product_info_list = company_2_category_products.apply(lambda row: f"Product Name: {row['product_name']}\nDetails: {row['details']}", axis=1).to_list()

            # combine all product details contained in one category into text 
            company_1_product_details = "\n".join(company_1_product_info_list)
            company_2_product_details = "\n".join(company_2_product_info_list) 

            # Format the prompt
            formatted_prompt = prompt.format(
                company_1=company_1,
                company_2=company_2,
                category=category,
                company_1_details=company_1_product_details,
                company_2_details=company_2_product_details,
            )
    
            response = chat_model.predict(formatted_prompt).strip() 

            # Append the data to the list
            comparison_data.append({
                "company_1": company_1,
                "company_2": company_2,
                "category": category,
                "company_1_details": company_1_product_details,
                "company_2_details": company_2_product_details,
                "comparison": response,
                "prompt": prompt.format(
                    company_1=company_1,
                    company_2=company_2,
                    category=category,
                    company_1_details=company_1_product_details,
                    company_2_details=company_2_product_details,
                )
            })
    print(f"comparison completed")
    print("="*100)
    comparison_data_df = pd.DataFrame(comparison_data)
    return comparison_data_df


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
    











