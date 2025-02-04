##### 1. Install the dependancies 
```bash
    poetry install
```

```bash
    poetry lock --no-update
```

##### 2. Enter poetry shell 
```bash
    poetry shell
```  

##### 3. Run pipelines 
```bash
    kedro run --pipeline pipeline_name
``` 
Check the ```pipeline_registry.py``` ( e.g., ```kedro run --pipeline categorization``` ) 
- current pipelines: company_data_preprocessing, categorization, evaluation_pipeline, poster_evaluation_pipeline, poster_comparison_pipeline  ( refer to ```pipeline_registry.py``` )

#### data catalog 
- Input prompts are in ```data/0_prompts```
    - every time you run the evaluation pipeline, the prompts will be versioned and saved in ```data/5_eval_tracking``` 
    - To update the prompts, change the prompts in the directory : ```data/0_propmts```.
    - Previous prompts can be retrieved from ```data/5_eval_tracking``` 
- All the generated data are versioned: crawled data, category data, category ground truth set
- Currently tracking the Evaluation score ( currently, ground truth agreement score ), prompts. 
- category_ground_truth_set is data generated from categorization pipeline, which should be manually corrected.
    - At the moment, the ground truth dataset is the same as the category data, as it is not the final dataset.
    - Used for evaluation along with the prompts used to generate category data.
- The categories listed in the pormpt are generated from the notebook "0. Generating_Categories.ipynb" 

#### experiment tracking 
- Change prompt in data/_poster_draft/prompts/comparison_prompt.txt 
- Run poster_comparison and poster_evaluation pipelines 
    - Each prompts are saved in ```data/_poster_draft/6_tracked_prompts```
    - Each evaluation result is saved in ```data/_poster_draft/5_comparison_evaluation_result``` 
- Run ```kedro viz run``` to see the change of metrics 

#### parameters 
- input urls 
- llm model options 

#### to-do and hoping-to-do : 
- Keep track of datasets and evaluation metric 
- Integrate the current functions into tools ( Use whosever method we are going to use, make use of agents )    
- Implement comparison BASE model   
- (Optionally)Integrate multi agents so that agents can interactively adjust the generated dataset.
    - example : https://colab.research.google.com/drive/1dM5uOGIqT_NYQJlmRrlaFuerpfEH0ecy?usp=sharing#scrollTo=Cpa1AE5bS7Js 
- Implement streamlit     
