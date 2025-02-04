"""
This is a boilerplate pipeline 'evaluation'
generated using Kedro 0.19.10
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import get_category_eval_golden_set, evaluate_gta_product_category, track_prompt_records


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(func=get_category_eval_golden_set,
             inputs=["human_insurance_classification_prompt", "category_ground_truth_set"],
             outputs="category_eval_golden_dataset"),
        node(func=evaluate_gta_product_category, 
             inputs=["params:llm_model_options", "system_insurance_classification_prompt", 
                     "human_insurance_classification_prompt" , "category_eval_golden_dataset"],
             outputs="tracking_gta_score"),
        node(func=track_prompt_records, 
             inputs=["system_insurance_classification_prompt", "human_insurance_classification_prompt"],
             outputs="tracking_categorization_prompts"),
    ])

# ground_truth_data is a category_data in the data catalog that is manually corrected 