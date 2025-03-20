from kedro.pipeline import Pipeline, node, pipeline
from .nodes import generate_reference_products, process_reference_data

def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=generate_reference_products,
            inputs="parameters:OPENAI_API_KEY",  # Reads only the parameters
            outputs="insurance_products_reference",  # This remains an in-memory dataset
            name="generate_insurance_products_node",
        ),
        node(
            func=process_reference_data,
            inputs=["insurance_products_reference", "parameters:OPENAI_API_KEY"],  # Pass the in-memory dataset
            outputs="insurance_reference_data",  # Save this to disk as defined in catalog.yml
            name="process_insurance_data_node",
        ),
    ])



