import os
import json
import numpy as np
import pandas as pd
import networkx as nx
from networkx.algorithms.clique import find_cliques
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# Global Constants
EMBED_CACHE = "embeddings_cache.npy"
CHUNK_SIZE = 512
MAX_TOKENS = 2000  # maximum tokens to consider per product text
MODEL_NAME = "sentence-transformers/multi-qa-distilbert-cos-v1"

############################################
# 1. Clustering Functions
############################################

def load_data(input_data):
    """
    Reads product JSON data and produces a list of product dictionaries.
    
    If input_data is a dict (from a PartitionedDataset), it iterates over its keys,
    reading each partition's JSON content. If it is a string, it treats it as a folder path.
    
    Each product dict contains:
      - company
      - category
      - product_id
      - product_name
      - details_list
    """
    all_products = []
    if isinstance(input_data, dict):
        # Process PartitionedDataset (dict: partition_name -> callable)
        for partition_name, file_reader in input_data.items():
            if partition_name.startswith("."):
                continue
            try:
                content = file_reader()
                company_data = json.loads(content)
            except Exception as e:
                print(f"Error reading or parsing partition {partition_name}: {e}")
                continue
            base_name = partition_name
            if base_name.endswith(".json"):
                base_name = os.path.splitext(base_name)[0]
            parts = base_name.split("_")
            if len(parts) >= 5:
                company = parts[-2].lower()
            else:
                company = base_name.lower()
            for product_id, product_info in company_data.items():
                product_name = product_info.get("product_name", "")
                category = product_info.get("category", "Uncategorized")
                details = product_info.get("details", "")
                details_list = [details] if isinstance(details, str) else details
                all_products.append({
                    "company": company,
                    "category": category,
                    "product_id": product_id,
                    "product_name": product_name,
                    "details_list": details_list
                })
    elif isinstance(input_data, str):
        # Process folder path (string)
        for filename in os.listdir(input_data):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(input_data, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                company_data = json.load(f)
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split("_")
            if len(parts) >= 5:
                company = parts[-2].lower()
            else:
                company = base_name.lower()
            for product_id, product_info in company_data.items():
                product_name = product_info.get("product_name", "")
                category = product_info.get("category", "Uncategorized")
                details = product_info.get("details", "")
                details_list = [details] if isinstance(details, str) else details
                all_products.append({
                    "company": company,
                    "category": category,
                    "product_id": product_id,
                    "product_name": product_name,
                    "details_list": details_list
                })
    else:
        raise TypeError("Expected input_data to be a dict or a string (folder path).")
    return all_products

def chunk_text(text: str, max_length=CHUNK_SIZE):
    tokens = text.split()
    chunks = []
    current = []
    for token in tokens:
        current.append(token)
        if len(current) >= max_length:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks

def build_embeddings(products, cache_path=EMBED_CACHE):
    if os.path.exists(cache_path):
        print(f"[INFO] Loading cached embeddings from '{cache_path}'...")
        return np.load(cache_path)
    print(f"[INFO] Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, device='cuda' if __import__('torch').cuda.is_available() else 'cpu')
    print("[INFO] Model loaded. Now computing embeddings...")
    all_embeddings = []
    for p in tqdm(products, desc="Embedding products"):
        text = p["product_name"] + "\n" + "\n".join(p["details_list"])
        tokens = text.split()[:MAX_TOKENS]
        text = " ".join(tokens)
        chunks = chunk_text(text, max_length=CHUNK_SIZE)
        if not chunks:
            emb_dim = model.get_sentence_embedding_dimension()
            all_embeddings.append(np.zeros(emb_dim))
            continue
        chunk_vectors = model.encode(chunks, show_progress_bar=False)
        product_embedding = np.mean(chunk_vectors, axis=0)
        all_embeddings.append(product_embedding)
    embeddings = np.array(all_embeddings)
    np.save(cache_path, embeddings)
    print(f"[INFO] Embeddings computed and cached at '{cache_path}'")
    return embeddings

def cluster_by_maximal_cliques(products, embeddings, threshold=0.7):
    """
    Constructs a similarity graph (only connecting products from different companies
    with cosine similarity >= threshold) per category and finds maximal cliques.
    Returns clusters that include products from different companies.
    """
    category_to_indexes = {}
    for i, p in enumerate(products):
        cat = p["category"]
        category_to_indexes.setdefault(cat, []).append(i)
    sims = cosine_similarity(embeddings)
    clusters = []
    for category, idxs in category_to_indexes.items():
        if len(idxs) < 2:
            continue
        G = nx.Graph()
        for i_ in idxs:
            G.add_node(i_)
        for i in range(len(idxs)):
            for j in range(i+1, len(idxs)):
                idx_i = idxs[i]
                idx_j = idxs[j]
                if products[idx_i]["company"] == products[idx_j]["company"]:
                    continue
                if sims[idx_i, idx_j] >= threshold:
                    G.add_edge(idx_i, idx_j)
        all_max_cliques = list(find_cliques(G))
        for clique in all_max_cliques:
            companies = set()
            valid = True
            for node in clique:
                comp = products[node]["company"]
                if comp in companies:
                    valid = False
                    break
                companies.add(comp)
            if valid and len(clique) >= 2:
                clusters.append({
                    "category": category,
                    "product_indexes": list(clique)
                })
    return clusters

def get_clusters_json(input_data, threshold: float = 0.75) -> str:
    """
    Clusters products from the input data (either a folder path or a dict from a PartitionedDataset)
    and returns a JSON string of clusters. Each cluster includes its ID, category, and detailed product info.
    """
    print(f"[INFO] Loading products...")
    products = load_data(input_data)
    print(f"[INFO] Loaded {len(products)} products total.")
    embeddings = build_embeddings(products)
    print("[INFO] Clustering by maximal cliques...")
    clusters = cluster_by_maximal_cliques(products, embeddings, threshold=threshold)
    print(f"[INFO] Found {len(clusters)} total clusters with threshold={threshold}.")
    output_data = []
    for i, cluster_obj in enumerate(clusters, start=1):
        cat = cluster_obj["category"]
        idxs = cluster_obj["product_indexes"]
        product_list = []
        for idx in idxs:
            prod = products[idx]
            product_list.append({
                "company": prod["company"],
                "product_id": prod["product_id"],
                "product_name": prod["product_name"],
                "category": prod["category"],
                "details_list": prod["details_list"]
            })
        output_data.append({
            "cluster_id": i,
            "category": cat,
            "products": product_list
        })
    clusters_json = json.dumps(output_data, indent=2, ensure_ascii=False)
    return clusters_json

############################################
# 2. JSON Format Conversion Node
############################################

def convert_clusters_format(clusters_json: str) -> str:
    """
    Converts clusters JSON to a new format containing only:
      - cluster_id
      - products: list of objects with 'company', 'product_name', and 'details_list'
    """
    clusters = json.loads(clusters_json)
    converted = []
    for cluster in clusters:
        new_cluster = {
            "cluster_id": cluster.get("cluster_id"),
            "products": []
        }
        for product in cluster.get("products", []):
            new_product = {
                "company": product.get("company"),
                "product_name": product.get("product_name"),
                "details_list": product.get("details_list")
            }
            new_cluster["products"].append(new_product)
        converted.append(new_cluster)
    converted_json = json.dumps(converted, indent=2, ensure_ascii=False)
    return converted_json

############################################
# 3. LLM-based Comparison Table Generation Node
############################################

def generate_comparison_tables(converted_clusters_json: str, comparison_prompt: str, openai_api_key: str) -> (dict, pd.DataFrame):
    """
    Generates Markdown comparison tables for each cluster using an LLM.
    
    Args:
        converted_clusters_json (str): JSON string of clusters in converted format.
        comparison_prompt (str): Prompt template containing [SYSTEM MESSAGE] and [USER MESSAGE] divider.
        openai_api_key (str): OpenAI API key.
    
    Returns:
        A tuple with:
          - A dictionary mapping filenames to Markdown table content.
          - A pandas DataFrame with evaluation data.
    """
    clusters = json.loads(converted_clusters_json)
    
    # Initialize the ChatOpenAI model
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)
    
    # Split the prompt template into system and user parts
    splitted = comparison_prompt.split("[USER MESSAGE]")
    if len(splitted) < 2:
        raise ValueError("The comparison prompt must contain a '[SYSTEM MESSAGE]' and a '[USER MESSAGE]' divider.")
    system_part = splitted[0].replace("[SYSTEM MESSAGE]", "").strip()
    user_part = splitted[1].strip()
    
    system_msg_template = SystemMessagePromptTemplate.from_template(system_part)
    
    comparisons = {}
    evaluation_data = []
    
    for cluster in clusters:
        cluster_id = cluster.get("cluster_id", "unknown")
        products = cluster.get("products", [])
        if not products:
            continue
        # In this example, category is not provided; set as "Uncategorized"
        category = "Uncategorized"
        products_text = ""
        company_names = []
        product_names = []
        for idx, prod in enumerate(products, start=1):
            company = prod.get("company", "N/A")
            product_name = prod.get("product_name", "N/A")
            details_list = prod.get("details_list", [])
            details = "\n".join(details_list)
            products_text += f"Product {idx}:\n"
            products_text += f"Company: {company}\n"
            products_text += f"Product Name: {product_name}\n"
            products_text += "Details:\n" + details + "\n\n"
            company_names.append(company)
            product_names.append(product_name)
        
        final_user_prompt = user_part.replace("{{CATEGORY}}", category).replace("{{PRODUCTS_TEXT}}", products_text)
        human_msg_template = HumanMessagePromptTemplate.from_template(final_user_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_msg_template, human_msg_template])
        messages = chat_prompt.format_messages()
        
        print(f"Generating comparison table for cluster {cluster_id} ...")
        response = llm(messages)
        md_table = response.content.strip()
        filename = f"comparison_cluster_{cluster_id}.md"
        comparisons[filename] = md_table
        
        evaluation_data.append({
            "cluster_id": cluster_id,
            "company_names": list(set(company_names)),
            "product_names": list(set(product_names)),
            "category": category,
            "products_text": products_text,
            "comparison": md_table
        })
        print(f"Generated comparison table for cluster {cluster_id}.")
    
    evaluation_df = pd.DataFrame(evaluation_data)
    return comparisons, evaluation_df

############################################
# 4. Markdown to Excel Conversion Node
############################################

def parse_markdown_table(md_text: str) -> pd.DataFrame:
    """
    Parses a Markdown table and converts it into a Pandas DataFrame.
    Expects a header row and a separator row.
    """
    lines = md_text.strip().split("\n")
    table_lines = [line.strip() for line in lines if line.strip().startswith("|") and line.strip().endswith("|")]
    if len(table_lines) < 3:
        return pd.DataFrame()
    header = table_lines[0].strip("|").split("|")
    header = [col.strip() for col in header]
    data_rows = table_lines[2:]
    parsed_data = []
    for row in data_rows:
        columns = row.strip("|").split("|")
        parsed_data.append([col.strip() for col in columns])
    return pd.DataFrame(parsed_data, columns=header)

def convert_md_to_excel(comparisons: dict) -> pd.DataFrame:
    """
    Converts Markdown tables from the comparisons dict into a single pandas DataFrame.
    Adds a 'source' column indicating the filename of each table.
    """
    df_list = []
    for filename, md in comparisons.items():
        # Skip files that are not markdown files
        if not filename.endswith(".md"):
            print(f"Skipping non-markdown file: {filename}")
            continue
        # If the value is callable (as in a PartitionedDataset), call it to get its content
        md_text = md() if callable(md) else md
        try:
            df = parse_markdown_table(md_text)
        except Exception as e:
            print(f"Error parsing markdown table from {filename}: {e}")
            continue
        if not df.empty:
            df["source"] = filename
            df_list.append(df)
        else:
            print(f"⚠ No valid table found in {filename}. Skipping...")
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        combined_df = pd.DataFrame()
    return combined_df


