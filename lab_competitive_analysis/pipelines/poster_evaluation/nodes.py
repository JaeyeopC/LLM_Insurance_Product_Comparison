"""
This is a boilerplate pipeline 'poster_evaluation'
generated using Kedro 0.19.10
"""

import os
import numpy as np
import openai
import pandas as pd  # Import pandas to fix the error
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from trulens.core import TruSession, Feedback
from trulens.feedback import GroundTruthAgreement
from trulens.providers.openai import OpenAI
# from trulens.providers.huggingface import Huggingface
from trulens.apps.custom import TruCustomApp, instrument

import matplotlib.pyplot as plt  # Fixed indentation error
from kedro_datasets.matplotlib import MatplotlibWriter  # Fixed indentation error


# [TODO] Add plots of the results based on the categories ( category 1: scores... / category 2: scores...) - bar plot  
def evaluate_comparison_output(comparison_df: pd.DataFrame, model_options: dict):
    authentication()
    provider = get_model(model_options)

    similiarity_score_list = []
    comprehensive_score_list = []
    groundedness_score_list = [] 

    # add combined information as 'companies_info' column 
    comparison_df['companies_info'] = comparison_df.apply(
        lambda row: f"""{row['company_1']} and {row['company_2']} comparison in {row['category']}: \n\n
        {row['company_1']} information : \n\n {row['company_1_details']}\n\n
        {row['company_2']} information : \n\n {row['company_2_details']}""", axis=1)
    
    # create golden set for gta evaluation 
    golden_set = (
        comparison_df[['companies_info', 'comparison']]
        .rename(columns={'companies_info': 'query', 'comparison': 'expected_response'})
        .to_dict("records")
    )

    gta = GroundTruthAgreement(golden_set, provider=provider)

    similarity_score_list = []
    comprehensiveness_score_list = []
    groundedness_score_list = []
    company_1_list = []
    company_2_list = []
    category_list = []
    total_company_number = len(comparison_df['company_1'].unique())
    for i in range(len(comparison_df)):
        print(f'evaluating comparison : {comparison_df["company_1"][i]} and {comparison_df["company_2"][i]} in {comparison_df["category"][i]}')
        try:
            similarity_score = gta.agreement_measure(
                prompt=comparison_df['companies_info'][i],
                response=comparison_df['comparison'][i]
            )[0]
        except Exception as e:
            print(f"An error occurred while processing similarity score at row {i}: {e}")
            similarity_score = 0

        try:
            comprehensiveness_score = provider.comprehensiveness_with_cot_reasons( # https://www.trulens.org/cookbook/use_cases/summarization_eval/#write-feedback-functions 
                source=comparison_df['companies_info'][i], # The source that should support the statement ( comapnies information )
                summary=comparison_df['comparison'][i], # Statement ( comparison result ) 
            )[0]
        except Exception as e:
            print(f"An error occurred while processing comprehensiveness score at row {i}: {e}")
            comprehensiveness_score = 0
            
        try:
            groundedness_score = provider.groundedness_measure_with_cot_reasons( # https://www.trulens.org/cookbook/use_cases/summarization_eval/#write-feedback-functions 
                source=comparison_df['companies_info'][i], # The source that should support the statement ( comapnies information )
                statement=comparison_df['comparison'][i], # Statement ( comparison result ) 
            )[0]
        except Exception as e:
            print(f"An error occurred while processing groundedness score at row {i}: {e}")
            groundedness_score = 0

        print(f'comparison between {comparison_df["company_1"][i]} and {comparison_df["company_2"][i]} in {comparison_df["category"][i]}')
        print(f'similarity_score : {similarity_score}, comprehensiveness_score : {comprehensiveness_score}, groundedness_score : {groundedness_score}')

        # track_evaluation_results(similarity_score, comprehensiveness_score, groundedness_score, comparison_df['company_1'][i], comparison_df['company_2'][i], comparison_df['category'][i])

        similarity_score_list.append(similarity_score)
        comprehensiveness_score_list.append(comprehensiveness_score)
        groundedness_score_list.append(groundedness_score)
        company_1_list.append(comparison_df['company_1'][i])
        company_2_list.append(comparison_df['company_2'][i])
        category_list.append(comparison_df['category'][i])
        
    print(f'evaluation completed')

    mean_score_dict = {
        'mean_similarity_score': np.mean(similarity_score_list),
        'mean_comprehensiveness_score': np.mean(comprehensiveness_score_list),
        'mean_groundedness_score': np.mean(groundedness_score_list),
        'data_length': len(comparison_df)
    }
  

    return mean_score_dict #, result_df
    

# Save the current prompt used for comparison
def save_current_prompt(comparison_prompt: str):
    return comparison_prompt


def authentication():
    load_dotenv() 
    OpenAI_key = os.getenv("OPENAI_API_KEY")
    # Huggingface_key = Huggingface() # for groundedness_measure_with_nli 

    if not OpenAI_key:
        raise ValueError("OpenAI API key not found. Please check your authentication key path.") 
    # if not Huggingface_key:
    #     raise ValueError("OpenAI API key not found. Please check your authentication key path.") 
    
def get_model(model_options: dict):
    authentication() 
    model_name = model_options["model_name"]
    temperature = model_options["temperature"]
    max_tokens = model_options["max_tokens"]

    # llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
    provider = OpenAI()
    return provider




# def track_evaluation_results(similarity_score, comprehensiveness_score, groundedness_score, company_1, company_2, category):
#     return {
#         'similarity_score': similarity_score,
#         'comprehensiveness_score': comprehensiveness_score,
#         'groundedness_score': groundedness_score,
#         'company_1': company_1,
#         'company_2': company_2,
#         'category': category
#     }