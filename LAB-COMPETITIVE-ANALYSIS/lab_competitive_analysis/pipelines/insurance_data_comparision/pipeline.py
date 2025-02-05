from kedro.pipeline import Pipeline, node, pipeline
from .nodes import create_product_comparisons


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=create_product_comparisons,
                inputs=["classified_product_details", "comparison_prompt", "categories_file", "params:openai_api_key"],
                outputs=["product_comparisons_markdowns","comparison_table_for_evaluation"],
                name="create_product_comparisons_node"
            ),
        ]
    )
