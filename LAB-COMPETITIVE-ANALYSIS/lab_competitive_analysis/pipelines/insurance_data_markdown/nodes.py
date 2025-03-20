from typing import Dict
from langchain.schema import Document
from langchain_community.document_transformers import Html2TextTransformer
from pathlib import Path


def transform_html_to_markdown(crawled_data_paths: Dict[str, str]) -> Dict[str, str]:
    html2text = Html2TextTransformer()
    cleansed_text = {}
    grouped_files = {}

    for path, file_reader in crawled_data_paths.items():
        company = path.split("/")[0]
        if company not in grouped_files:
            grouped_files[company] = []
        grouped_files[company].append((path, file_reader))

    for company, files in grouped_files.items():
        for path, file_reader in files:
            html_content = file_reader()
            document = Document(page_content=html_content, metadata={"source": path})
            transformed_doc = html2text.transform_documents([document])[0]

            markdown_content = transformed_doc.page_content

            cleansed_key = path.replace(".html", ".md")
            cleansed_text[cleansed_key] = markdown_content

    return cleansed_text