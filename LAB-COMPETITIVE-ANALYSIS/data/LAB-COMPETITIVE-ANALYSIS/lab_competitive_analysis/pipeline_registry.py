"""Project pipelines."""

from kedro.pipeline import Pipeline, pipeline
# import pipelines.data_classification.pipeline as data_classification
# import pipelines.data_processing.pipeline as data_processing
# import pipelines.data_refinement.pipeline as data_refinement
# import pipelines.reference_data.pipeline as reference_data

import pipelines.insurance_data_crawling.pipeline as insurance_data_crawling
import pipelines.insurance_data_filtering.pipeline as insurance_data_filtering
import pipelines.insurance_data_markdown.pipeline as insurance_data_markdown
import pipelines.insurance_data_extraction.pipeline as insurance_data_extraction
import pipelines.insurance_data_classification.pipeline as insurance_data_classification
import pipelines.insurance_data_comparision.pipeline as insurance_data_comparision
import pipelines.insurance_data_evaluation.pipeline as insurance_data_evaluation

# sometimes kedro does not recognize the pipeline.
# this is a workaround to register the pipeline manually
# kedro run --pipeline "name of pipeline", e.g., "kedro run --pipeline insurance_data_comparison"
def register_pipelines() -> dict[str, Pipeline]:
    # data_classification_pipeline = data_classification.create_pipeline()
    # data_processing_pipeline = data_processing.create_pipeline()
    # data_refinement_pipeline = data_refinement.create_pipeline()
    # reference_data_pipeline = reference_data.create_pipeline()
    
    insurance_data_crawling_pipeline = insurance_data_crawling.create_pipeline()
    insurance_data_filtering_pipeline = insurance_data_filtering.create_pipeline()
    insurance_data_markdown_pipeline = insurance_data_markdown.create_pipeline()
    insurance_data_extraction_pipeline = insurance_data_extraction.create_pipeline()
    insurance_data_classification_pipeline = insurance_data_classification.create_pipeline()
    insurance_data_comparison_pipeline = insurance_data_comparision.create_pipeline()
    insurance_data_evaluation_pipeline = insurance_data_evaluation.create_pipeline()
    
    pipelines = {
        "__default__": insurance_data_comparison_pipeline + insurance_data_evaluation_pipeline,
        "insurance_data_comparison": insurance_data_comparison_pipeline,
        "insurance_data_evaluation": insurance_data_evaluation_pipeline,
        "insurance_data_classification": insurance_data_classification_pipeline,
        "insurance_data_extraction": insurance_data_extraction_pipeline,
        "insurance_data_filtering": insurance_data_filtering_pipeline,
        "insurance_data_markdown": insurance_data_markdown_pipeline,
        "insurance_data_crawling": insurance_data_crawling_pipeline,
        # "data_classification": data_classification_pipeline,
        # "data_processing": data_processing_pipeline,
        # "data_refinement": data_refinement_pipeline,
        # "reference_data": reference_data_pipeline
    }
    
    return pipelines

# original code
# from kedro.framework.project import find_pipelines
# from kedro.pipeline import Pipeline, pipeline
# from .pipelines.insurance_data_crawling.pipeline import create_pipeline as crawl_company_websites
# from .pipelines.insurance_data_filtering.pipeline import create_pipeline as filter_product_pages
# from .pipelines.insurance_data_markdown.pipeline import create_pipeline as transform_html_to_markdown
# from .pipelines.insurance_data_extraction.pipeline import create_pipeline as extract_full_details
# from .pipelines.insurance_data_classification.pipeline import create_pipeline as classify_products
# from .pipelines.insurance_data_comparision.pipeline import create_pipeline as create_product_comparisons
# from .pipelines.insurance_data_evaluation.pipeline import create_pipeline as create_evaluation_node

# def register_pipelines() -> dict[str, Pipeline]:
#     """Register the project's pipelines.

#     Returns:
#         A mapping from pipeline names to ``Pipeline`` objects.
#     """
#     combined_pipeline = pipeline(
#         [
#             crawl_company_websites(),
#             filter_product_pages(),
#             transform_html_to_markdown(),
#             extract_full_details(),
#             classify_products(),
#             create_product_comparisons(),
#             create_evaluation_node()
#         ]
#     )
#     pipelines = find_pipelines()
#     pipelines["__default__"] = combined_pipeline

#     return pipelines  # Added return statement to return the pipelines dictionary
