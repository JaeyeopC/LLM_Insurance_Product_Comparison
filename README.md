# What is this for?

This folder should be used to store configuration files used by Kedro or by separate tools.

This file can be used to provide users with instructions for how to reproduce local configuration with their own credentials. You can edit the file however you like, but you may wish to retain the information below and add your own section in the section titled **Instructions**.

## Local configuration

The `local` folder should be used for configuration that is either user-specific (e.g. IDE configuration) or protected (e.g. security keys).

> *Note:* Please do not check in any local configuration to version control.

## Base configuration

The `base` folder is for shared configuration, such as non-sensitive and project-related configuration that may be shared across team members.

WARNING: Please do not put access credentials in the base configuration folder.

## Find out more
You can find out more about configuration from the [user guide documentation](https://docs.kedro.org/en/stable/configuration/configuration_basics.html).

## How to use

- Change the ```openai_api_key``` in ```parameters.yml``` to your own key
-  ```poetry install``` : install the dependencies
- ```poetry shell``` : activate the virtual environment
- ```poetry run kedro run``` : run the whole pipeline the order specified in ```__default__```  in ```pipeline_registry.py```
    - ```poetry run kedro run --node <node_name>``` : run the specific node
    - ```poetry run kedro run --pipeline <pipeline_name>``` : run the specific pipeline
    -  ```poetry run kedro run --pipeline <pipeline_name> --nodes <node_name>``` : run the specific node in the specific pipeline
- data pipeline names : ```pipeline_registry.py``` 
- input/output data : ```conf/base/catlog.yml``` and ```pipeline/nodes.py``` 
- supported data types : see [kedro_datasets](https://docs.kedro.org/projects/kedro-datasets/en/kedro-datasets-6.0.0/api/kedro_datasets.html) 
---
## Evaluation pipeline for reference 
Please, when changing the classification and comparison pipeline, change the evaluation pipeline to fit the new structure...  
- categoization evaluation 
    - input
        - output from the ```insurance_data_classification``` pipeline ( as one csv file ) 
            - Once the scope is set, one of output will be used as a ground truth dataset by correcting the categories manually  
            - Then the prompt used for categorization with the variable used will be fed into LLM, and the category output of the LLM will be compared to the categories in the ground truth dataset 
        - categorization prompt
- comparison evaluation 
    - input
        - output from the ```insurance_data_comparision``` pipeline ( as one csv file )
        - comparison prompt 
--- 
[TODO] 
1. Add Pydantic models and tools for LLMs  - Add a pipeline for generating the prompt for the LLM
2. Implement Lang Graph ( multi agents )

---
[TODO] Articles 
- ReAct Article https://dottxt-ai.github.io/outlines/latest/cookbook/react_agent/
- Tool Calling : https://python.langchain.com/docs/concepts/tool_calling/  
- Structured Chat : https://python.langchain.com/v0.1/docs/modules/agents/agent_types/structured_chat/ 
- Lang Graph ReAct : https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/#define-nodes-and-edges 
- Lang Graph Guide: https://www.ionio.ai/blog/a-comprehensive-guide-about-langgraph-code-included 
- 랭체인(langchain) + 정형데이터(CSV, Excel) - ChatGPT 기반 데이터분석 (4) : https://teddylee777.github.io/langchain/langchain-tutorial-04/ 
- 랭체인(langchain) + 웹사이트 크롤링 - 웹사이트 문서 요약 (5) : https://teddylee777.github.io/langchain/langchain-tutorial-05/ 
- LLMs를 활용한 문서 요약 가이드: Stuff, Map-Reduce, Refine 방법 총정리 - 테디노트 : https://teddylee777.github.io/langchain/summarize-chain/
- 자동화된 메타데이터 태깅으로 문서의 메타데이터(metadata) 생성 및 자동 라벨링 : https://teddylee777.github.io/langchain/metadata-tagger/