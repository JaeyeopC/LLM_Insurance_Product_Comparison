from kedro.pipeline import Pipeline, node, pipeline
from .nodes import extract_full_details

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=extract_full_details,
            inputs=["filtered_product_markdowns", "extract_full_details_prompt", "params:openai_api_key"],
            outputs="extracted_product_details",
            name="extract_full_details_node"
        )
    ])
