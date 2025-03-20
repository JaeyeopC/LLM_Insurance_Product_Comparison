import os
import json
import html2text

def process_json_files(input_directory, output_directory):
    # Initialize the HTML to Text converter
    html_converter = html2text.HTML2Text()
    html_converter.ignore_links = True  # Adjust as needed

    # Dictionary to hold data per company
    company_data = {}

    # Walk through the directory structure
    for dirpath, dirnames, filenames in os.walk(input_directory):
        for filename in filenames:
            if filename.lower().endswith('.json'):
                json_file_path = os.path.join(dirpath, filename)
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Extract the content to process
                content_to_process = data.get('content', [])

                # Convert content to HTML string
                html_content = convert_content_to_html(content_to_process)

                # Use html2text to convert HTML to text
                refined_text = html_converter.handle(html_content)

                # Extract subtitles and tables from content
                subtitles = extract_subtitles(content_to_process)
                tables = extract_tables(content_to_process)

                # Prepare the refined data
                refined_data = {
                    'company_name': data.get('company_name', ''),
                    'title': data.get('title', ''),
                    'page_name': data.get('page_name', ''),
                    'refined_text': refined_text.strip(),
                    'subtitles': subtitles,
                    'tables': tables
                }

                company_name = refined_data['company_name']
                if not company_name:
                    company_name = 'Unknown'

                # Initialize company entry if not present
                if company_name not in company_data:
                    company_data[company_name] = {
                        'company_name': company_name,
                        'pages': []
                    }

                # Append refined data to company's pages
                company_data[company_name]['pages'].append(refined_data)

    # After processing all files, write one JSON per company
    for company_name, data in company_data.items():
        # Write the output JSON file per company
        output_file_path = os.path.join(output_directory, f"{company_name}.json")
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print(f"Created output file for company: {company_name}")

def convert_content_to_html(content_list):
    # Helper function to recursively convert content to HTML
    def content_to_html(content):
        html_parts = []
        for element in content:
            if 'type' in element:
                if element['type'] == 'heading':
                    level = element.get('level', 1)
                    text = element.get('text', '')
                    html_parts.append(f"<h{level}>{text}</h{level}>")
                    if 'content' in element:
                        html_parts.append(content_to_html(element['content']))
                elif element['type'] == 'paragraph':
                    text = element.get('text', '')
                    html_parts.append(f"<p>{text}</p>")
                elif element['type'] == 'list':
                    list_type = 'ol' if element.get('list_type') == 'ordered' else 'ul'
                    items_html = ''
                    for item in element.get('items', []):
                        # If item is a string, wrap it in <li>
                        if isinstance(item, str):
                            items_html += f"<li>{item}</li>"
                        else:
                            item_content = content_to_html(item.get('content', []))
                            items_html += f"<li>{item_content}</li>"
                    html_parts.append(f"<{list_type}>{items_html}</{list_type}>")
                elif element['type'] == 'table':
                    table_html = "<table>"
                    data = element.get('data', [])
                    for row in data:
                        table_html += "<tr>"
                        for cell in row:
                            table_html += f"<td>{cell}</td>"
                        table_html += "</tr>"
                    table_html += "</table>"
                    html_parts.append(table_html)
                elif element['type'] == 'image':
                    src = element.get('src', '')
                    alt = element.get('alt', '')
                    html_parts.append(f"<img src='{src}' alt='{alt}' />")
                elif element['type'] == 'link':
                    href = element.get('href', '')
                    text = element.get('text', '')
                    html_parts.append(f"<a href='{href}'>{text}</a>")
                elif element['type'] == 'text':
                    text = element.get('text', '')
                    html_parts.append(text)
                else:
                    # Process any other types recursively
                    if 'content' in element:
                        html_parts.append(content_to_html(element['content']))
            else:
                # If the element is text
                if 'text' in element:
                    html_parts.append(element['text'])
        return ''.join(html_parts)

    html_content = content_to_html(content_list)
    # Wrap in <html> tags to make it valid HTML
    return "<html><body>" + html_content + "</body></html>"

def extract_subtitles(content_list):
    subtitles = []

    def extract_from_content(content):
        for element in content:
            if element.get('type') == 'heading':
                level = element.get('level', 1)
                if level > 1:
                    text = element.get('text', '')
                    subtitles.append(text)
            if 'content' in element:
                extract_from_content(element['content'])
            elif element.get('type') == 'list':
                for item in element.get('items', []):
                    if isinstance(item, dict):
                        extract_from_content([item])
    extract_from_content(content_list)
    return subtitles

def extract_tables(content_list):
    tables = []

    def extract_from_content(content):
        for element in content:
            if element.get('type') == 'table':
                table_data = element.get('data', [])
                tables.append(table_data)
            if 'content' in element:
                extract_from_content(element['content'])
            elif element.get('type') == 'list':
                for item in element.get('items', []):
                    if isinstance(item, dict):
                        extract_from_content([item])
    extract_from_content(content_list)
    return tables

if __name__ == '__main__':
    # Set the input directory where your preprocessed JSON files are located
    input_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/2_data'

    # Set the output directory where refined JSON files will be saved
    output_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/3_refined_data'

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Process all JSON files
    process_json_files(input_directory, output_directory)

    print("All files have been processed.")
