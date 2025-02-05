from kedro.pipeline import Pipeline, node, pipeline
from .nodes import filter_product_pages

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=filter_product_pages,
                inputs=["insrances_crawled_data", "filter_prompt", "params:openai_api_key"],
                outputs=["filtered_product_pages", "csv_output"],
                name="filter_product_pages_node",
            )
        ]
    )
