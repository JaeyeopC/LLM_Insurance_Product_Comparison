"""
This is a boilerplate pipeline 'evaluation'
generated using Kedro 0.19.10
"""
import os
import time
import numpy as np
import pandas as pd  # Import pandas to fix the error 
from dotenv import load_dotenv
from openai import OpenAI
from trulens.apps.custom import TruCustomApp, instrument
from trulens.core import TruSession, Feedback
from trulens.feedback import GroundTruthAgreement
from trulens.providers.openai import OpenAI as fOpenAI # specify TruLens OpenAI wrapper 
from pydantic import BaseModel, Field 
from langchain_core.output_parsers import PydanticOutputParser 


# #instrumented classification evaluation app. Every evaluation loop, app generates a response to original query and TruLens gta compares it with the ground truth data
class CategorizationApp:
    @instrument
    def categorize(self, categorization_query):
        authentication()
        oai_client = OpenAI()
        response = (
            oai_client.chat.completions.create(
                temperature=0,
                model="gpt-4o",
                messages=[
                    {
                        "role": "user", 
                        "content": categorization_query 
                    }
                ]
            )
            .choices[0].message.content
        )
        return response



def comparison_evaluation(comparison_evaluation_table: pd.DataFrame, openai_api_key: str) -> pd.DataFrame:
    """
    This function evaluates comparison tasks by calculating similarity, comprehensiveness, and groundedness scores
    for each entry in the provided comparison evaluation table. It uses OpenAI's API to perform these evaluations.
    Parameters:
    - comparison_evaluation_table (pd.DataFrame): A DataFrame containing the comparison data with columns 'company_details', 'comparison', 'company_names', and 'category'.
    - openai_api_key (str): The API key for accessing OpenAI services.
    Returns:
    - pd.DataFrame: A DataFrame containing the calculated scores for similarity, comprehensiveness, and groundedness,
      along with the company names and categories.
    """
    
    print("evaluating comparison tasks...") 
    
    # get the openai api key 
    authentication()
    tru_openai_model = fOpenAI(api_key=openai_api_key)
    
    # initialize lists to store scores and company names 
    similarity_score_list = []
    comprehensiveness_score_list = []
    groundedness_score_list = []
    company_list = []
    category_list = []
    
    # use a shorter variable name
    comparison_df = comparison_evaluation_table

    # build golden set for ground truth agreement(similarity) score 
    golden_set = (
        comparison_evaluation_table[['company_details', 'comparison']]
        .rename(columns={'company_details': 'query', 'comparison': 'expected_response'})
        .to_dict("records")
    )

    # initialize ground truth agreement score function with ground truth set 
    gta = GroundTruthAgreement(golden_set, provider=fOpenAI(api_key=openai_api_key))
    
    # evaluate the comparison table in three different metrics. output : [0] : score, [1] : LLM cot reasons 
    for i in range(len(comparison_df)):
        start = time.time()
        print(f'{i+1}/{len(comparison_df)} | comparison between {comparison_df["company_names"][i]:>20} in {comparison_df["category"][i]}')
        
        try:
            similarity_score = gta.agreement_measure(
                prompt=comparison_df['company_details'][i],
                response=comparison_df['comparison'][i]
            )[0] 
        except Exception as e:
            print(f"An error occurred while processing similarity score at row {i}: {e}")
            similarity_score = np.nan

        try:
            comprehensiveness_score = tru_openai_model.comprehensiveness_with_cot_reasons(
                source=comparison_df['company_details'][i],
                summary=comparison_df['comparison'][i],
            )[0]
        except Exception as e:
            print(f"An error occurred while processing comprehensiveness score at row {i}: {e}")
            comprehensiveness_score = np.nan

        try:
            groundedness_score = tru_openai_model.groundedness_measure_with_cot_reasons(
                source=comparison_df['company_details'][i],
                statement=comparison_df['comparison'][i],
            )[0]
        except Exception as e:
            print(f"An error occurred while processing groundedness score at row {i}: {e}")
            groundedness_score = np.nan
            
        end = time.time()
        
        print(f'similarity_score: {similarity_score:.4f}, comprehensiveness_score: {comprehensiveness_score:.4f}, groundedness_score: {groundedness_score:.4f} | time: {end - start:.2f} seconds')    
        print("=========================================================================")

        similarity_score_list.append(similarity_score)
        comprehensiveness_score_list.append(comprehensiveness_score)
        groundedness_score_list.append(groundedness_score)
        company_list.append(comparison_df['company_names'][i])
        category_list.append(comparison_df['category'][i])

    # store results in a dataframes
    comparison_eval_result_df = pd.DataFrame({
        'similarity_score': similarity_score_list,
        'comprehensiveness_score': comprehensiveness_score_list,
        'groundedness_score': groundedness_score_list,
        'company_list': company_list,
        'category': category_list
    })

    print('=== Comparison result evaluation is completed ===')
    return comparison_eval_result_df 


def categorization_evaluation(categorization_ground_truth_table: pd.DataFrame, categories_file: str, classification_prompt: str, openai_api_key: str) -> pd.DataFrame:
    """
    Perform categorization evaluation by comparing model responses to ground truth data.
    Args:
        categorization_ground_truth_table (pd.DataFrame): dataframe result from "insurance_data_classification" pipeline, containing "company", "category", "product_name", "details" 
        classification_evaluation_table (pd.DataFrame): dataframe result from "insurance_data_classification" pipeline, containing "company", "category", "product_name", "details" 
        categories_file (str): String content of the categories file, each line representing a category.
        classification_prompt (str): Template string for classification prompts.
        openai_api_key (str): API key for OpenAI services.
    Returns:
        pd.DataFrame: DataFrame containing similarity scores, original categories, and model response categories.
    """
    authentication()
    print("Evaluating categorization tasks...")

    # Initialize categorization app
    categorization_app = CategorizationApp()

    # Predefined category list
    category_list = [line.strip() for line in categories_file.splitlines() if line.strip()]

    # Build completed query by formatting
    categorization_ground_truth_table['complete_query'] = categorization_ground_truth_table.apply(
        lambda row: classification_prompt.format(
            categories=category_list,
            product_name=row['product_name'],
            details=row['details']
        ),
        axis=1
    )

    # Queries to be used for categorization app, expected answers to be compared to responses from app
    golden_set = pd.DataFrame({
        'query': categorization_ground_truth_table['complete_query'],
        'expected_response': categorization_ground_truth_table['category']
    }).to_dict("records")

    # Initialize ground truth agreement score function with ground truth set
    gta = GroundTruthAgreement(golden_set, provider=fOpenAI(api_key=openai_api_key))

    categorization_score_list = []
    categorization_ground_truth_category_list = []
    categorization_response_category_list = []

    for i, row in enumerate(golden_set):
        start = time.time()
        
        try:
            response = categorization_app.categorize(categorization_query=row['query'])
            score = gta.agreement_measure(
                prompt=row['query'],
                response=response  # LLM response
            )
        except Exception as e:
            print(f"An error occurred while processing similarity score at row {i}: {e}")
            similarity_score = np.nan

        similarity_score = score[0]
        ground_truth_category = score[1]['ground_truth_response']
        llm_response_category = response

        categorization_score_list.append(similarity_score)
        categorization_ground_truth_category_list.append(ground_truth_category)
        categorization_response_category_list.append(llm_response_category)

        end = time.time()
        print(f"{i+1}/{len(golden_set)} : similarity_score: {similarity_score:<2} | ground truth: {ground_truth_category:<30} | received: {llm_response_category:<30} | time: {end - start:.2f} seconds")

    classification_eval_result_df = pd.DataFrame({
        'similarity_score': categorization_score_list,
        'original_category': categorization_ground_truth_category_list,
        'responsed_category': categorization_response_category_list
    })

    print('=== Categorization evaluation is completed ===')
    return classification_eval_result_df



def track_comparison_result_mean_metrics(comparison_eval_result_table: pd.DataFrame, categorization_eval_result_table: pd.DataFrame) -> dict:
    """
    Calculate and return the mean metrics for comparison and categorization evaluation results.
    Args:
        comparison_eval_result_table (pd.DataFrame): DataFrame containing evaluation results for comparisons, with columns for similarity, comprehensiveness, and groundedness scores.
        categorization_eval_result_table (pd.DataFrame): DataFrame containing evaluation results for categorization, with a column for similarity scores.
    Returns:
        dict: A dictionary containing the mean scores for similarity, comprehensiveness, and groundedness from the comparison evaluation, 
              and the mean similarity score from the categorization evaluation.
    """
    print('storing the mean metrics...')
    
    # Fill NaN values with 0
    comparison_eval_result_table['similarity_score'].fillna(0, inplace=True)
    comparison_eval_result_table['comprehensiveness_score'].fillna(0, inplace=True)
    comparison_eval_result_table['groundedness_score'].fillna(0, inplace=True)
    categorization_eval_result_table['similarity_score'].fillna(0, inplace=True)
    
    # Return the mean metrics
    return {
        'comp_mean_similarity_score': np.mean(comparison_eval_result_table['similarity_score']),
        'comp_mean_comprehensiveness_score': np.mean(comparison_eval_result_table['comprehensiveness_score']),
        'comp_mean_groundedness_score': np.mean(comparison_eval_result_table['groundedness_score']),
        'categ_mean_similarity_score': np.mean(categorization_eval_result_table['similarity_score'])
    }



# return and version the category prompt used for categorization for this dataset
def track_category_prompt(category_prompt):
    return category_prompt

# return and version the comparison prompt used for comparison for this dataset
def track_comparison_prompt(comparison_prompt):
    return comparison_prompt

# register OpenAI API Key with .env 
def authentication():
    load_dotenv() 
    OpenAI_key = os.getenv("OPENAI_API_KEY")





























# defines a pydantic model for app
# class Category_List(BaseModel):
#     category: str = Field(
#         description=
#         """
#             category list: 
#                 Risikolebensversicherung, Gemischte Lebensversicherung, Rentenversicherung, Berufsunfähigkeitsversicherung, 
#                 Pflegerentenversicherung, Krankenversicherung, Dread Disease Versicherung, Grundfähigkeitsversicherung, Pflegekostenversicherung, 
#                 Pflegetagegeldversicherung, Haftpflichtversicherung, Betriebsunterbrechungsversicherung, Hausratversicherung, 
#                 Gebäudeversicherung, Geschäftsinhaltsversicherung, Gewerbeversicherung, Rücklaufversicherung, Bauleistungsversicherung, 
#                 Maschinenkasko und Maschinenbruchversicherung, Kreditversicherung, Vertrauensschadenversicherung, Montageversicherung, Elementarversicherung, 
#                 Unfallversicherung, Reiseversicherung, Transportversicherung, Private Arbeitslosenversicherung, Tierversicherung, Fahrerschutzversicherung, Rechtsschutzversicherung
#         """
#     )



# class CategorizationApp:
#     def __init__(self):
#         self.parser = PydanticOutputParser(pydantic_object=Category_List)
#         self.format_inst = self.parser.get_format_instructions()
        
#     @instrument
#     def categorize(self, categorization_query):
#         authentication()
#         client = OpenAI()
#         response = (
#             client.beta.chat.completions.parse(
#                 temperature=0,
#                 messages=[
#                     {
#                         "role": "user", 
#                         "content": categorization_query + "\n\n" + self.format_inst
#                     }
#                 ],
#                 response_format= Category_List
#             )
#             .choices[0].message.parsed
#         )
#         return response.category
