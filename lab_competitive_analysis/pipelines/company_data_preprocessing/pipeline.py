"""
This is a boilerplate pipeline 'company_data_preprocessing'
generated using Kedro 0.19.10
"""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import crawl_comapany_urls, save_processed_company_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(func=crawl_comapany_urls, 
                 inputs=["params:search_options"],
                 outputs="unprocessed_crawled_data"),
             node(func=save_processed_company_data, 
                 inputs=["unprocessed_crawled_data"],
                 outputs="processed_crawled_data"),
        ]
    )

