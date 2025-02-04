"""
This is a boilerplate pipeline 'evaluation'
generated using Kedro 0.19.10
"""
# ground truth agreement : https://www.trulens.org/getting_started/quickstarts/groundtruth_evals/ 
# groundedness : https://github.com/truera/trulens/issues/1271 

import os
from dotenv import load_dotenv
import pandas as pd  # Import pandas to fix the error 
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser 

from trulens.core import TruSession
from trulens.core import Feedback
from trulens.feedback import GroundTruthAgreement
from trulens.providers.openai import OpenAI
from trulens.apps.custom import TruCustomApp

from trulens.apps.custom import instrument
import openai 

from pprint import pprint 


class response_model(BaseModel):  # Renamed class to avoid conflict with variable name
    answer: str = Field(..., description="answer to the question") 

class classify_category_model(BaseModel):
    category: str = Field(description="determine the category of the insurance product",
                          enum = [                             
                             "Term Life Insurance", "Whole Life Insurance", "Pension Insurance", "Disability Insurance", 
                             "Long-Term Care Pension Insurance", "Health Insurance", "Critical Illness Insurance", "Basic Ability Insurance", 
                             "Long-Term Care Cost Insurance", "Long-Term Care Daily Allowance Insurance", "Liability Insurance", 
                             "Business Interruption Insurance", "Home Contents Insurance", "Building Insurance", "Business Property Insurance", 
                             "Commercial Insurance", "Loan Repayment Insurance", "Construction Performance Insurance", 
                             "Machinery Breakdown and Machinery Insurance", "Credit Insurance", "Fidelity Guarantee Insurance", "Erection Insurance", 
                             "Natural Disaster Insurance", "Accident Insurance", "Travel Insurance", "Transport Insurance", "Private Unemployment Insurance", 
                             "Pet Insurance", "Driver Protection Insurance", "Legal Protection Insurance"]
    )

class CategorizationApp:
    def __init__(self, model_options: dict, classify_sys_prompt: str, classify_human_prompt: str):
        self.model_options = model_options
        self.classify_sys_prompt = classify_sys_prompt
        self.classify_human_prompt = classify_human_prompt
        self.parser = PydanticOutputParser(pydantic_object=classify_category_model)
        self.format_inst = self.parser.get_format_instructions()

    @instrument
    def categorize(self, classify_human_prompt=None):
        if classify_human_prompt is None:
            classify_human_prompt = self.classify_human_prompt

        authentication()
        client = openai.OpenAI()
        response = (
            client.beta.chat.completions.parse(
                model=self.model_options["model_name"],
                messages=[
                    {
                        "role": "system", 
                        "content": self.classify_sys_prompt.format(format_instructions=self.format_inst)
                    },
                    {
                        "role": "user", 
                        "content": classify_human_prompt 
                    }
                ],
                response_format=classify_category_model
            )
            .choices[0].message.parsed
        )
        return response.category


def get_category_eval_golden_set(classify_human_prompt: str, data: pd.DataFrame):
    query_dic = {'query': []} 
    for _, row in data.iterrows():
        query_dic['query'].append(classify_human_prompt.format(company=row['company'], title=row['title'], content=row['content']))
    
    category_eval_golden_dataset = pd.DataFrame({
        'query': query_dic['query'],
        'expected_response': data['category']
    })
    
    return category_eval_golden_dataset 


def evaluate_gta_product_category(llm_model_options: dict, classify_sys_prompt: str, classify_human_prompt: str, category_eval_golden_dataset: pd.DataFrame):
    authentication()
    session = TruSession()
    session.reset_database() 
    provider = OpenAI(model_engine=llm_model_options["model_name"])

    category_eval_app = CategorizationApp(llm_model_options, classify_sys_prompt, classify_human_prompt)
    gta = GroundTruthAgreement(category_eval_golden_dataset, provider=provider)
    
    gta_eval_scores = [] 
    ground_truth_list = [] 
    response_category_list = [] 

    for _, row in category_eval_golden_dataset.iterrows():
        response = category_eval_app.categorize(classify_human_prompt = row['query'])
        gta_score = gta.agreement_measure(
            prompt = row['query'],
            response = category_eval_app.categorize(classify_human_prompt = row['query'])
            )
        
        gta_eval_scores.append(gta_score[0])
        ground_truth_list.append(gta_score[1]['ground_truth_response'])
        response_category_list.append(response)

        print(f"score: {gta_score[0]:<2} | ground truth: {gta_score[1]['ground_truth_response']:<30} | received: {response:<30}")
    
    # write the evaluation values to a csv file 
    result_df = pd.DataFrame({
        'gta_eval_scores': gta_eval_scores,
        'ground_truth': ground_truth_list,
        'response_category': response_category_list
    })
    
    result_df.to_csv("data/5_eval_tracking/evaluation_table.csv", index=False)

    gta_metric_score = sum(gta_eval_scores) / len(category_eval_golden_dataset)  # get the gta score as an average score 
    print(f"GTA score: {gta_metric_score}")

    return {"gta_metric_score" : gta_metric_score} 

# save the current prompt records for tracking
def track_prompt_records(classify_sys_prompt: str, classify_human_prompt: str):
    return {"classify_sys_prompt" : classify_sys_prompt, "classify_human_prompt" : classify_human_prompt}

def authentication():
    load_dotenv() 
    OpenAI_key = os.getenv("OPENAI_API_KEY")

    if not OpenAI_key:
        raise ValueError("OpenAI API key not found. Please check your authentication key path.") 



# TODO : Add evaluation for comparison 



# def category_eval_session_recorder(llm_model_options: dict, classify_sys_prompt: str, classify_human_prompt: str, data: pd.DataFrame):
#     authentication()
#     session = TruSession()
#     session.reset_database() 
#     provider = OpenAI(model_engine="gpt-4o")

#     category_eval_golden_dataset = data
#     category_eval_app = CategorizationApp(llm_model_options, classify_sys_prompt, classify_human_prompt)
#     gta = GroundTruthAgreement(category_eval_golden_dataset, provider=provider)

#     f_groundtruth = Feedback(
#         gta.agreement_measure, name="Ground Truth Similarity (LLM)"
#     ).on_input_output()
    
#     categoty_eval_recorder = TruCustomApp(
#         category_eval_app,
#         app_name="category evaluation",
#         app_version="v1",
#         feedbacks=f_groundtruth
#     ) 

#     for row in category_eval_golden_dataset:
#         with categoty_eval_recorder:
#             category_eval_app.categorize(human_input_query = row['query'])

#     session.get_leaderboard()