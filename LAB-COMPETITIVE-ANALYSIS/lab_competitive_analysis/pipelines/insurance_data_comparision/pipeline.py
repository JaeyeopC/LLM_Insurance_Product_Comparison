from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    get_clusters_json,
    convert_clusters_format,
    generate_comparison_tables,
    convert_md_to_excel
)

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=get_clusters_json,
                inputs=["classified_product_details", "params:clustering_threshold"],
                outputs="clusters_by_clique_json",
                name="cluster_products_node"
            ),
            node(
                func=convert_clusters_format,
                inputs="clusters_by_clique_json",
                outputs="converted_clusters_json",
                name="convert_clusters_format_node"
            ),
            node(
                func=generate_comparison_tables,
                inputs=["converted_clusters_json", "comparison_prompt", "params:openai_api_key"],
                outputs=["product_comparisons_markdowns", "comparison_table_for_evaluation"],
                name="generate_comparison_tables_node"
            ),
            node(
                func=convert_md_to_excel,
                inputs="product_comparisons_markdowns",
                outputs="final_result_table_comparision",
                name="convert_md_to_excel_node"
            )
        ]
    )
