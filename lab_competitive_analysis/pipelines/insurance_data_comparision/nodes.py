import os
import json
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from typing import Dict, Tuple
import pandas as pd 


def create_product_comparisons(
    classified_products: Dict[str, callable],
    prompt_file: str,
    categories_file: str,
    openai_api_key: str,
) -> Tuple[Dict[str, str], pd.DataFrame]: 
    """
    Generate product comparison tables for multiple companies.

    Args:
        classified_products (Dict[str, callable]): A dictionary where keys are company names and values are JSON readers for classified products.
        prompt_file (str): The file path of the prompt content as a string.
        categories_file (str): The categories file content as a string.
        openai_api_key (str): The OpenAI API key.

    Returns:
        Dict[str, str]: Comparison tables as Markdown content keyed by category.
    """
    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)

    # Load the categories
    categories = [line.strip() for line in categories_file.splitlines() if line.strip()]

    # Load product details for all companies
    company_products = {}
    for company, product_reader in classified_products.items():
        company_data = json.loads(product_reader())  # Call reader to get JSON content
        company_products[company] = company_data

    # Create a LangChain prompt
    prompt = PromptTemplate(
        input_variables=["category", "company_info"],
        template=prompt_file,
    )

    # Dictionary to hold comparison tables
    comparisons = {}

    # List for comparison evaluation dataframe - keeps data per category coupled with comparison
    comparison_evaluation_data_list = []

    for category in categories:
        # Collect product details for the category across companies
        company_names = []
        company_details = []
        company_product_names = [] 
        for company, products in company_products.items():
            for product_name, product_data in products.items():
                if product_data.get("category") == category:
                    # Allow for arbitrary keys
                    product_info = "\n".join([
                        f"{key}: {str(item)}" if not isinstance(item, list) else f"{key}: {", ".join(map(str, item))}"
                        for key, item in product_data.items() if key != "category"
                    ])
                    company_details.append(f"information von {company}:\n{product_info}\n")
                    company_names.append(company)
                    company_product_names.append(product_name)

        # Skip if less than two companies have matching products for the category
        if len(company_details) < 2:
            print(f"No sufficient comparisons for category: {category}")
            continue

        # Format the prompt with collected details
        formatted_prompt = prompt.format(
            category=category,
            company_info="\n".join(company_details),
        )

        # Generate the Markdown table
        try:
            response = chat_model.predict(formatted_prompt).strip()

            # Save the Markdown table with .md extension
            comparisons[f"{category.replace(' ', '_').lower()}.md"] = response
            print(f" Generated Markdown table for {category}")
            
            comparison_evaluation_data_list.append({
                "company_names": set(company_names),
                "product_names": set(company_product_names),
                "category": category,
                "company_details": company_details,
                "comparison": response
            })
        except Exception as e:
            print(f" Error generating comparison for {category}: {e}")

    comparison_table_for_evaluation = pd.DataFrame(comparison_evaluation_data_list)

    return comparisons, comparison_table_for_evaluation
