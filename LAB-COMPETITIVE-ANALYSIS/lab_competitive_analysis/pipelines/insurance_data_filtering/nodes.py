import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate


def filter_product_pages(input_partitioned_data, prompt_file, openai_api_key):
    """
    Filters product pages for multiple companies and saves only the product pages.

    Args:
        input_partitioned_data (PartitionedDataset): The input PartitionedDataset containing HTML files organized by company.
        prompt_file (str): The prompt file content as a string.
        openai_api_key (str): The OpenAI API key.

    Returns:
        dict: Filtered product pages ready for saving to the output directory.
        str: Consolidated CSV summary as a single string.
    """
    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)

    # Prepare output data structures
    filtered_product_pages = {}
    csv_summary = "company_name,page_name,product\n"

    # Create the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt_file)
    ])

    # Group files by company
    grouped_files = {}
    for partition_name, partition_data in input_partitioned_data.items():
        company_name = partition_name.split("/")[0]  # Extract company name from the folder structure
        if company_name not in grouped_files:
            grouped_files[company_name] = {}
        grouped_files[company_name][partition_name] = partition_data

    # Process each company
    for company_name, company_files in grouped_files.items():
        filtered_data = {}

        # Process each file for the company
        for file_path, file_data in company_files.items():
            formatted_prompt = chat_prompt.format_messages(filename=file_path)
            try:
                # Get the model's response
                response = chat_model(formatted_prompt).content.strip()
                is_product = "yes" in response.lower()  # Determine if it's a product page

                # Write result to the CSV string
                csv_summary += f"{company_name},{file_path},{'yes' if is_product else 'no'}\n"

                # If it's a product page, add the original content to the filtered dataset
                if is_product:
                    filtered_data[file_path] = file_data()
            except Exception as e:
                print(f"Error processing {file_path} for company {company_name}: {e}")

        # Save filtered data for the company
        filtered_product_pages.update(filtered_data)

    return filtered_product_pages, csv_summary
