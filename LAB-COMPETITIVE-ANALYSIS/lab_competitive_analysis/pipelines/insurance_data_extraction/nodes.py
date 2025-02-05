from typing import Dict
import json
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

def extract_full_details(cleansed_data_paths: Dict[str, str], prompt_file: str, openai_api_key: str) -> Dict[str, str]:
    """
    Extract product details from Markdown files using a language model.

    Args:
        cleansed_data_paths (Dict[str, str]): A dictionary of Markdown file paths and readers.
        prompt_file (str): The prompt file content as a string.
        openai_api_key (str): The OpenAI API key.

    Returns:
        Dict[str, str]: A dictionary where keys are company names and values are JSON strings of extracted details.
    """
    grouped_files = {}
    company_details = {}

    # Group files by company
    for path, file_reader in cleansed_data_paths.items():
        company = path.split("/")[0]
        if company not in grouped_files:
            grouped_files[company] = []
        grouped_files[company].append((path, file_reader))

    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)

    # Create a LangChain prompt
    prompt = PromptTemplate(
        input_variables=["content"],  # Only content is needed
        template=prompt_file
    )

    # Process files for each company
    for company, files in grouped_files.items():
        company_products = {}

        for path, file_reader in files:
            try:
                # Read the Markdown content
                markdown_content = file_reader()

                # Format the prompt with content
                formatted_prompt = prompt.format(content=markdown_content)
                response = chat_model.predict(formatted_prompt).strip()

                # Parse response into product name and details
                product_name = None
                details = []
                for line in response.splitlines():
                    if line.startswith("Produktname:"):
                        product_name = line.replace("Produktname:", "").strip()
                    elif line.startswith("- "):  # Capture bullet-pointed details
                        details.append(line[2:].strip())

                # Store the extracted data
                company_products[path] = {
                    "product_name": product_name,
                    "details": details
                }

                print(f"Extracted from {path}:\n{company_products[path]}\n")

            except Exception as e:
                print(f"Error processing file {path}: {e}")

        # Serialize the company's products to JSON
        company_details[company] = json.dumps(company_products, ensure_ascii=False, indent=4)

    return company_details
