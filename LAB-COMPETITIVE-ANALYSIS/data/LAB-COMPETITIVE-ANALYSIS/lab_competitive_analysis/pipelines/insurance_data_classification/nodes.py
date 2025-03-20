from typing import Dict
import json
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import pandas as pd
from pydantic import BaseModel, Field 


class Category(BaseModel):
    category: str = Field(
        description=(
            """
            category list: 
                Risikolebensversicherung, Gemischte Lebensversicherung, Rentenversicherung, Berufsunfähigkeitsversicherung, 
                Pflegerentenversicherung, Krankenversicherung, Dread Disease Versicherung, Grundfähigkeitsversicherung, Pflegekostenversicherung, 
                Pflegetagegeldversicherung, Haftpflichtversicherung, Betriebsunterbrechungsversicherung, Hausratversicherung, 
                Gebäudeversicherung, Geschäftsinhaltsversicherung, Gewerbeversicherung, Rücklaufversicherung, Bauleistungsversicherung, 
                Maschinenkasko und Maschinenbruchversicherung, Kreditversicherung, Vertrauensschadenversicherung, Montageversicherung, Elementarversicherung, 
                Unfallversicherung, Reiseversicherung, Transportversicherung, Private Arbeitslosenversicherung, Tierversicherung, Fahrerschutzversicherung, Rechtsschutzversicherung
            """
        )
    )

def classify_products(product_details: Dict[str, callable], prompt_file: str, categories_file: str, openai_api_key: str) -> Dict[str, str]:
    """
    Classify products into categories for multiple companies using a language model.

    Args:
        product_details (Dict[str, callable]): A dictionary where keys are company names, and values are callables to read product details JSON.
        prompt_file (str): The prompt file content as a string.
        categories_file (str): The categories file content as a string.
        openai_api_key (str): The OpenAI API key.

    Returns:
        Dict[str, str]: A dictionary where keys are company names, and values are JSON strings of classified products.
    """
    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)

    # Load the categories
    categories = [line.strip() for line in categories_file.splitlines() if line.strip()]

    # Create a LangChain prompt
    prompt = PromptTemplate(
        input_variables=["product_name", "details", "categories"],
        template=prompt_file
    )

    # Dictionary to hold classified products for each company
    classified_products_per_company = {}

    # List to build classification evaluation dataframe
    classification_evaluation_data_list = []

    # Process each company's product details
    for company, company_data_reader in product_details.items():
        try:
            # Read the product details JSON string
            company_data_json = company_data_reader()  
            company_data = json.loads(company_data_json)
            classified_products = {}

            for product_file, product_data in company_data.items():
                product_name = product_data.get("product_name")

                # Validate product_name and skip if None or empty
                if not product_name:
                    print(f"Skipping product in {product_file} for {company} due to missing product_name.")
                    continue

                product_name = product_name.strip()
                details = "\n".join(product_data.get("details", [])) 


                # Format the prompt
                formatted_prompt = prompt.format(
                    product_name=product_name,
                    details=details,
                    categories="\n".join(categories)
                )

                # Use the chat model to classify the product
                try:
                    response = chat_model.predict(formatted_prompt).strip()
                    if response in categories:  # Check if the response matches a category
                        classified_products[product_file] = {
                            "product_name": product_name,
                            "category": response,
                            "details": product_data["details"]
                        }
                    else:
                        print(f"No match for: {product_name} in {company}")

                        classified_products[product_file] = {
                            "category": response,
                            "product_name": product_name,
                            "product_details": product_data["details"]
                        }
                    
                    classification_evaluation_data_list.append({
                        "company": company,
                        "product_name": product_name,
                        "category": response,
                        "details": product_data["details"]
                    })

                except Exception as e:
                    print(f"Error processing {product_name} for {company}: {e}")

            # Serialize the classified products for the company to JSON
            classified_products_per_company[company] = json.dumps(classified_products, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing company {company}: {e}")
    
    # Table to be used as a ground truth dataset for evaluation, see data catalog 
    classification_table_for_evaluation = pd.DataFrame(classification_evaluation_data_list)

    return classified_products_per_company, classification_table_for_evaluation
