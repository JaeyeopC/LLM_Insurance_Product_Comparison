"""
This is a boilerplate pipeline 'insurance_data_pipeline'
generated using Kedro 0.19.10
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import comparison_evaluation, track_comparison_result_mean_metrics, track_category_prompt, track_comparison_prompt, categorization_evaluation


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=comparison_evaluation,
                inputs=["comparison_table_for_evaluation", "params:openai_api_key"],
                outputs="eval_result_table_comparision",
                name="comparison_eval_node"
            ),
            node(
                func=categorization_evaluation,
                inputs=["categorization_ground_truth_table", "categories_file", "classification_prompt", "params:openai_api_key"],
                outputs="eval_result_table_categorization",
                name="categorization_eval_node"
            ),
            node(
                func=track_comparison_result_mean_metrics,
                inputs=["eval_result_table_comparision", "eval_result_table_categorization"],
                outputs="track_comparison_eval_mean_metric",
                name="track_comparison_metric_result_node"
            ),
            node(
                func=track_category_prompt,
                inputs="classification_prompt",
                outputs="track_category_prompt",
                name="track_category_prompt"
            ),
            node(
                func=track_comparison_prompt,
                inputs="comparison_prompt",
                outputs="track_comparison_prompt",
                name="track_comparison_prompt"
            ),
        ]
    )
