"""
This is a boilerplate pipeline 'categorization'
generated using Kedro 0.19.10
"""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import check_product, save_category_data, save_ground_truth_set


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(func=check_product, 
             inputs=["params:llm_model_options", "system_product_check_prompt" , 
                     "human_product_check_prompt" , "processed_crawled_data"],
             outputs="product_only_data"),
        node(func=save_category_data, 
             inputs=["params:llm_model_options", "system_insurance_classification_prompt" , 
                     "human_insurance_classification_prompt" , "product_only_data"],
             outputs="category_data"),
        node(func=save_ground_truth_set,
             inputs="category_data",
             outputs="category_ground_truth_set"),
    ])
