import os
import json
from bs4 import BeautifulSoup, Comment
import re

def extract_content_from_html(html_data):
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_data, 'html.parser')

    # Remove comments and unwanted elements
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    for unwanted in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside', 'iframe']):
        unwanted.decompose()

    # Page title
    title = soup.title.string.strip() if soup.title else None

    # Collect metadata
    metadata = {}
    for meta in soup.find_all('meta'):
        meta_name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
        meta_content = meta.get('content', '')
        if meta_name and meta_content:
            metadata[meta_name] = meta_content

    # Initialize content structure
    content = {
        'title': title,
        'metadata': metadata,
        'content': []
    }

    # Function to extract content recursively
    def extract_element_content(elements):
        extracted_content = []
        for element in elements:
            if isinstance(element, str):
                text = element.strip()
                if text:
                    extracted_content.append({'text': text})
                continue
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading_level = int(element.name[1])
                heading_text = element.get_text(strip=True)
                if heading_text:
                    extracted_content.append({
                        'type': 'heading',
                        'level': heading_level,
                        'text': heading_text
                    })
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    extracted_content.append({'type': 'paragraph', 'text': text})
            elif element.name in ['ul', 'ol']:
                list_type = 'ordered' if element.name == 'ol' else 'unordered'
                items = [li.get_text(strip=True) for li in element.find_all('li')]
                extracted_content.append({'type': 'list', 'list_type': list_type, 'items': items})
            elif element.name == 'table':
                table_data = []
                headers = [th.get_text(strip=True) for th in element.find_all('th')]
                if headers:
                    table_data.append(headers)
                for row in element.find_all('tr'):
                    cells = row.find_all('td')
                    if cells:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data.append(row_data)
                extracted_content.append({'type': 'table', 'data': table_data})
            elif element.name == 'img':
                img_src = element.get('src', '')
                img_alt = element.get('alt', '')
                if img_src or img_alt:
                    extracted_content.append({'type': 'image', 'src': img_src, 'alt': img_alt})
            elif element.name == 'a':
                href = element.get('href', '')
                link_text = element.get_text(strip=True)
                if href or link_text:
                    extracted_content.append({'type': 'link', 'href': href, 'text': link_text})
            elif element.name == 'blockquote':
                quote_text = element.get_text(strip=True)
                if quote_text:
                    extracted_content.append({'type': 'blockquote', 'text': quote_text})
            elif element.name == 'code':
                code_text = element.get_text(strip=True)
                if code_text:
                    extracted_content.append({'type': 'code', 'code': code_text})
            else:
                # Recursively process child elements
                child_elements = element.contents
                if child_elements:
                    extracted_content.extend(extract_element_content(child_elements))
        return extracted_content

    # Start extracting from the body
    body = soup.body
    if body:
        content['content'] = extract_element_content(body.contents)
    else:
        # If no body, extract from the whole document
        content['content'] = extract_element_content(soup.contents)

    return content

def process_html_files(root_directory, output_directory):
    # Walk through the directory structure
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.lower().endswith('.html') or filename.lower().endswith('.htm'):
                html_file_path = os.path.join(dirpath, filename)
                try:
                    with open(html_file_path, 'r', encoding='utf-8') as file:
                        html_data = file.read()
                except UnicodeDecodeError:
                    # Try with different encoding if utf-8 fails
                    with open(html_file_path, 'r', encoding='ISO-8859-1') as file:
                        html_data = file.read()

                # Extract content from HTML
                extracted_content = extract_content_from_html(html_data)

                # Include company name and page name
                relative_path = os.path.relpath(html_file_path, root_directory)
                path_parts = relative_path.split(os.sep)
                if len(path_parts) >= 2:
                    company_name = path_parts[0]
                else:
                    company_name = 'Unknown'
                page_name = os.path.splitext(filename)[0]

                # Add company name and page name to the extracted content
                extracted_content['company_name'] = company_name
                extracted_content['page_name'] = page_name

                # Determine the output path
                output_subdir = os.path.join(output_directory, os.path.dirname(relative_path))
                os.makedirs(output_subdir, exist_ok=True)
                output_file_path = os.path.join(output_subdir, page_name + '.json')

                # Save the extracted content to JSON file
                with open(output_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(extracted_content, json_file, indent=4, ensure_ascii=False)

                print(f"Processed {html_file_path} -> {output_file_path}")

if __name__ == '__main__':
    # Set the root directory where your HTML files are located
    root_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/data/01_company_crawled_data'

    # Set the output directory where JSON files will be saved
    output_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/2_data'

    # Process all HTML files
    process_html_files(root_directory, output_directory)

    print("All files have been processed.")
