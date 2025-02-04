"""
This is a boilerplate pipeline 'poster_comparison'
generated using Kedro 0.19.10
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import convert_json_to_csv, compare_products


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(func=convert_json_to_csv,
             inputs=["params:classification_json_data_dir"],
             outputs="detail_calassified_csv_data"),
        node(func=compare_products, 
             inputs=["detail_calassified_csv_data", "poster_comparison_prompt", 
                     "params:predefined_category_list" , "params:llm_model_options"],
             outputs="comparison_scv_data"),
    ])