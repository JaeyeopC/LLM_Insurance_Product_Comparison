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
    print("Initialized ChatOpenAI model.")

    # Prepare output data structures
    filtered_product_pages = {}
    csv_summary = "company_name,page_name,product\n"

    # Create the chat prompt from the provided prompt content
    chat_prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt_file)
    ])
    print("Chat prompt created from the provided prompt file.")

    # Group files by company
    grouped_files = {}
    for partition_name, partition_data in input_partitioned_data.items():
        # Extract company name from the partition path; assuming the format is "company/..."
        company_name = partition_name.split("/")[0]
        if company_name not in grouped_files:
            grouped_files[company_name] = {}
        grouped_files[company_name][partition_name] = partition_data
    print(f"Grouped files by company: {list(grouped_files.keys())}")

    # Process each company
    for company_name, company_files in grouped_files.items():
        print(f"\nProcessing company: {company_name}")
        filtered_data = {}

        # Process each file for the company
        for file_path, file_data in company_files.items():
            print(f"  Processing file: {file_path}")
            formatted_prompt = chat_prompt.format_messages(filename=file_path)
            try:
                # Get the model's response
                response = chat_model(formatted_prompt).content.strip()
                print(f"    Model response for {file_path}: {response}")
                is_product = "yes" in response.lower()  # Determine if it's a product page

                # Write result to the CSV string
                csv_line = f"{company_name},{file_path},{'yes' if is_product else 'no'}"
                csv_summary += csv_line + "\n"
                print(f"    CSV entry added: {csv_line}")

                # If it's a product page, add the original content to the filtered dataset
                if is_product:
                    filtered_data[file_path] = file_data()
                    print("    File marked as product. Added to filtered data.")
                else:
                    print("    File is not a product page.")
            except Exception as e:
                print(f"Error processing {file_path} for company {company_name}: {e}")

        # Update the filtered product pages with the company's filtered data
        filtered_product_pages.update(filtered_data)
        print(f"Completed processing company: {company_name}")

    print("Completed filtering all companies.")
    return filtered_product_pages, csv_summary
