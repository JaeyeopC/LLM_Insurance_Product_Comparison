"""Project pipelines."""

# from kedro.framework.project import find_pipelines
# from kedro.pipeline import Pipeline


# def register_pipelines() -> dict[str, Pipeline]:
#     """Register the project's pipelines.

#     Returns:
#         A mapping from pipeline names to ``Pipeline`` objects.
#     """
#     pipelines = find_pipelines()
#     pipelines["__default__"] = sum(pipelines.values())
#     return pipelines


from kedro.pipeline import Pipeline
import pipelines.company_data_preprocessing as company_data_preprocessing
import pipelines.categorization.pipeline as categorization 
import pipelines.evaluation as evaluation 
import pipelines.poster_evaluation as poster_evaluation
import pipelines.poster_comparison as poster_comparison


def register_pipelines() -> dict[str, Pipeline]:
    company_data_preprocessing_pipeline = company_data_preprocessing.create_pipeline()
    categorization_pipeline = categorization.create_pipeline()
    evaluation_pipeline = evaluation.create_pipeline()
    poster_evaluation_pipeline = poster_evaluation.create_pipeline()
    poster_comparison_pipeline = poster_comparison.create_pipeline()
    return {
        "__default__": company_data_preprocessing_pipeline + categorization_pipeline + evaluation_pipeline + poster_evaluation_pipeline + poster_comparison_pipeline,
        "company_data_preprocessing": company_data_preprocessing_pipeline,
        "categorization": categorization_pipeline,
        "evaluation": evaluation_pipeline,
        "poster_evaluation": poster_evaluation_pipeline,
        "poster_comparison": poster_comparison_pipeline
    }
