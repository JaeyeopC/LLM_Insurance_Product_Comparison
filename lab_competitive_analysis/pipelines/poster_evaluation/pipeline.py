"""
This is a boilerplate pipeline 'poster_evaluation'
generated using Kedro 0.19.10
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import evaluate_comparison_output, save_current_prompt#, plot_results_per_category


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(func=evaluate_comparison_output,
             inputs=["comparison_scv_data", "params:llm_model_options"],
            #  outputs=["comparison_evaluation_result", "result_df"]),
            outputs="comparison_evaluation_result"),
        node(func=save_current_prompt,
             inputs="poster_comparison_prompt",
             outputs="tracked_comparison_prompt"),
        # node(func=plot_results_per_category,
        #      inputs="result_df",
        #      outputs="output_plot")
    ])