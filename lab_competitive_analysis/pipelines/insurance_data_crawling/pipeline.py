from kedro.pipeline import Pipeline, node, pipeline
from .nodes import crawl_company_websites

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=crawl_company_websites,
            inputs=["params:companies"],
            outputs="insrances_crawled_data",
            name="crawl_companies_node",
        ),
    ])
