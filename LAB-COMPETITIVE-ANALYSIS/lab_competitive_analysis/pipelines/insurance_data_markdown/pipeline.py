from kedro.pipeline import Pipeline, node, pipeline
from .nodes import transform_html_to_markdown

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=transform_html_to_markdown,
            inputs="filtered_product_pages",
            outputs="filtered_product_markdowns",
            name="transform_html_to_markdown_node"
        )
    ])
