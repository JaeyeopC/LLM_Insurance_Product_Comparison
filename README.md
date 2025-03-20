# Leveraging LLM Pipelines to Generate Product Comparison Data

## Overview
This project presents a proof-of-concept for an LLM-driven market analysis system, specifically designed to generate structured insurance product comparisons across multiple companies in Germany. By leveraging advanced prompting techniques and evaluation metrics, we aim to enhance the accuracy, consistency, and comprehensiveness of LLM-generated product comparison data.

## Name 

## Features
- **Automated Data Processing**: Uses a Kedro-based data pipeline for efficient and reproducible data collection, filtering, and processing.
- **Advanced Prompting Techniques**: Implements role-based, iterative, structured output, and constraint-based prompting to improve product classification and comparison.
- **LLM-as-a-Judge Evaluation**: Utilizes TruLens metrics (Groundedness, Comprehensiveness, and GroundTruthAgreement) to assess the quality of LLM-generated comparisons.
- **Scalable Product Comparison Generation**: Compares similar insurance products from multiple companies using structured embeddings and cosine similarity.

## Repository Structure
```
NLP Competitive Market Analysis/
│── .viz/
│── conf/
│── data/
│   ├── 1_insurances_crawled_data/
│   ├── 2_filtered_product_pages/
│   ├── 3_filtered_product_markdowns/
│   ├── 4_extracted_product_details/
│   ├── 5_classified_product_details/
│   ├── 6_product_comparisons_markdowns/
│   ├── 8_evaluation/
│── lab_competitive_analysis/
│   ├── pipelines/
│   │   ├── insurance_data_classification/
│   │   ├── insurance_data_comparison/
│   │   ├── insurance_data_crawling/
│   │   ├── insurance_data_evaluation/
│   │   ├── insurance_data_extraction/
│   │   ├── insurance_data_filtering/
│   │   ├── insurance_data_markdown/
│   │   ├── reference_data/
│── notebooks/
│── tests/
│── pyproject.toml
│── README.md
│── poetry.lock

```

## Methodology
1. **Data Collection**: Crawling insurance company websites to collect relevant product data.
2. **Filtering & Classification**: Removing irrelevant content and categorizing products using LLM-based classification.
3. **Product Comparison Generation**: Structuring comparisons using advanced prompting techniques.
4. **Evaluation Metrics**: Assessing comparison reliability using LLM-as-a-Judge frameworks.

## Technologies Used
- **Kedro**: For pipeline orchestration and data management.
- **GPT-4o**: As the primary LLM for classification and comparison generation.
- **TruLens**: For evaluating LLM-generated output quality.
- **BeautifulSoup**: For web scraping and HTML parsing.
- **Python & Jupyter Notebooks**: For experimentation and analysis.

## Installation & Setup
### Prerequisites
- Python 3.8+
- Kedro
- Jupyter Notebook
- Required dependencies (see `requirements.txt`)

### Installation
```bash
# Clone the repository
git clone <repository_url>
cd <repository_directory>

# Install dependencies
pip install -r requirements.txt

# Run Kedro pipeline
kedro run
```

## Usage
- **Install Poetry dependencies**: `poetry install`
- **Freeze the current dependencies**: `poetry lock --no-update`
- **Enter poetry shell**: `poetry shell`
- **Run Data Pipeline**: `kedro run`
- **Run individual pipelines**: `kedro run --pipeline pipeline_name`
- **Visualize Pipeline**: `kedro viz`
- **Experiment with Prompts**: Modify `prompt_config.json` for custom prompt engineering.
- **Evaluate Results**: Run evaluation scripts under `evaluation/`.

## Results & Findings
- Advanced classification prompts improve comprehensiveness but may reduce specificity.
- LLM-as-a-Judge metrics effectively measure factual alignment and completeness.
- Combining structured prompting with metric-based evaluation enhances product comparison reliability.

## Future Improvements
- Integrating more advanced CoT-based prompting techniques.
- Expanding dataset coverage to additional insurance providers.
- Exploring alternative evaluation metrics to further optimize quality.

## Contributors
- **Khalil Chikhaoui**
- **Jaeyeop Chung**
- **Umut Ekin Gezer**
- **Advisor: Dr. Gerhard Johann Hagerer**

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
This work was conducted as part of the **Social Computing Research Group** at the **TUM School of Computation, Information and Technology**, Technical University of Munich.
