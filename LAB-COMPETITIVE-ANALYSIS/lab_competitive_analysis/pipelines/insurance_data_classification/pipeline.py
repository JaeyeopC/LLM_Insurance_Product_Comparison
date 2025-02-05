from kedro.pipeline import Pipeline, node, pipeline
from .nodes import classify_products


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=classify_products,
                inputs=["extracted_product_details", "classification_prompt", "categories_file", "params:openai_api_key"],
                outputs=["classified_product_details", "classification_table_for_evaluation"],
                name="classify_products_node",
            ),
        ]
    )
