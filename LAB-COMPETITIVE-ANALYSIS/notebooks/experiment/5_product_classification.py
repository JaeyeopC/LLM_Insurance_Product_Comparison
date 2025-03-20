import os
import json
import nltk
from nltk.corpus import stopwords
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from tqdm import tqdm

# Ensure the stopwords are downloaded
nltk.download('stopwords')


def load_reference_data(reference_path: str) -> List[str]:
    """Load reference insurance product names from a JSON file."""
    with open(reference_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    product_names = [item["product_name"] for item in data]
    return product_names


def translate_product_names(product_names: List[str], translation_mapping: Dict[str, str]) -> List[str]:
    """Translate product names using a predefined mapping."""
    return [translation_mapping.get(name.lower(), name) for name in product_names]


def load_company_data(input_directory: str) -> List[Dict]:
    """Load company data from JSON files in a directory."""
    company_data = []
    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                company = json.load(f)
                for page in company.get("pages", []):
                    company_data.append({
                        "company": company["company_name"],
                        "title": page.get("title", ""),
                        "refined_text": page.get("refined_text", "")
                    })
    return company_data


def compute_semantic_similarity(titles: List[str], translated_names: List[str]) -> Dict[str, str]:
    """
    Compute semantic similarity between titles and translated product names using TF-IDF and cosine similarity.
    """
    # Get German stopwords
    german_stopwords = stopwords.words('german')

    # Initialize TfidfVectorizer with German stopwords
    vectorizer = TfidfVectorizer(stop_words=german_stopwords)
    title_vectors = vectorizer.fit_transform(titles + translated_names)
    title_matrix = title_vectors[:len(titles)]
    product_matrix = title_vectors[len(titles):]
    
    similarities = cosine_similarity(title_matrix, product_matrix)
    best_matches = {}

    for idx, row in enumerate(similarities):
        best_idx = row.argmax()
        if row[best_idx] > 0.3:  # Adjust similarity threshold
            best_matches[titles[idx]] = translated_names[best_idx]

    return best_matches


def classify_titles(data: List[Dict], translated_names: List[str], threshold: float = 0.3) -> List[Dict]:
    """Classify titles based on semantic similarity with reference product names."""
    titles = [page['title'] for page in data if page['title'] and page['title'].strip()]
    semantic_matches = compute_semantic_similarity(titles, translated_names)

    classified_pages = []
    for page in data:
        title = page.get('title', '')
        if title in semantic_matches:
            page['classified_product'] = semantic_matches[title]
            classified_pages.append(page)

    return classified_pages


def save_classified_data(classified_data: List[Dict], output_directory: str):
    """Save classified data into JSON files, grouped by company and product."""
    os.makedirs(output_directory, exist_ok=True)
    grouped_data = {}

    for page in classified_data:
        company = page['company']
        product = page['classified_product']
        if company not in grouped_data:
            grouped_data[company] = {}
        if product not in grouped_data[company]:
            grouped_data[company][product] = []
        grouped_data[company][product].append(page)

    for company, products in grouped_data.items():
        company_dir = os.path.join(output_directory, company)
        os.makedirs(company_dir, exist_ok=True)
        for product, pages in products.items():
            product_filename = f"{product.replace(' ', '_').lower()}.json"
            product_filepath = os.path.join(company_dir, product_filename)
            with open(product_filepath, "w", encoding="utf-8") as f:
                json.dump(pages, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(pages)} pages to {product_filepath}")


def main():
    reference_path = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/4_insurance_reference_data.json'
    input_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/3_refined_data'
    output_directory = '/Users/umutekingezer/Desktop/NLP/nlp-competitive-market-analysis/nlp-competitive-market-analysis-kedro-project/experiment/5_classified_company_data'

    # Load reference product names
    product_names = load_reference_data(reference_path)
    print(f"Loaded {len(product_names)} insurance product names from reference data.")

    # Translate product names to German using a basic mapping or a manual translation dictionary
    translation_mapping = {}  # Define your mapping here, e.g., {"building insurance": "Gebäudeversicherung"}
    translated_product_names = translate_product_names(product_names, translation_mapping)
    print(f"Translated {len(translated_product_names)} product names to German.")

    # Load company data
    company_data = load_company_data(input_directory)
    print(f"Loaded {len(company_data)} pages from company data.")

    # Classify titles
    classified_pages = classify_titles(company_data, translated_product_names)
    print(f"Classified {len(classified_pages)} pages.")

    # Save classified data
    save_classified_data(classified_pages, output_directory)


if __name__ == "__main__":
    main()
