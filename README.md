
## How to use
1. Change the ```openai_api_key``` in ```parameters.yml``` to your own key
2. install the dependencies 
```bash
    poetry install
``` 
3. activate the poetry virtual environment
```bash
    poetry shell
```
4. run the pipeline : pipeline names are defined in ```pipeline_registry.py```  

4.1. run the whole pipeline
```bash
    poetry run kedro run
```
4.2. run specific pipelines 
```bash
    poetry run kedro run --pipeline <pipeline_name> 
```
4.3. run specific nodes from a sepcific pipeline
```bash
    poetry run kedro run --pipeline <pipeline_name> --nodes <node_name>
```
- run
5. For input output data : refer to ```conf/base/catalog.yml``` and other yml files in ```conf/base```
- Supported data types : see [kedro_datasets](https://docs.kedro.org/projects/kedro-datasets/en/kedro-datasets-6.0.0/api/kedro_datasets.html) 
--- 
[TODO] 
1. Add Pydantic models and tools for LLMs  - Add a pipeline for generating the prompt for the LLM
2. Implement Lang Graph ( multi agents )

- ReAct Article https://dottxt-ai.github.io/outlines/latest/cookbook/react_agent/
- Tool Calling : https://python.langchain.com/docs/concepts/tool_calling/  
- Structured Chat : https://python.langchain.com/v0.1/docs/modules/agents/agent_types/structured_chat/ 
- Lang Graph ReAct : https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/#define-nodes-and-edges 
- Lang Graph Guide: https://www.ionio.ai/blog/a-comprehensive-guide-about-langgraph-code-included 
- 랭체인(langchain) + 정형데이터(CSV, Excel) - ChatGPT 기반 데이터분석 (4) : https://teddylee777.github.io/langchain/langchain-tutorial-04/ 
- 랭체인(langchain) + 웹사이트 크롤링 - 웹사이트 문서 요약 (5) : https://teddylee777.github.io/langchain/langchain-tutorial-05/ 
- LLMs를 활용한 문서 요약 가이드: Stuff, Map-Reduce, Refine 방법 총정리 - 테디노트 : https://teddylee777.github.io/langchain/summarize-chain/
- 자동화된 메타데이터 태깅으로 문서의 메타데이터(metadata) 생성 및 자동 라벨링 : https://teddylee777.github.io/langchain/metadata-tagger/
---
[TODO]
- Documentation : Add Description for input and output for each pipeline