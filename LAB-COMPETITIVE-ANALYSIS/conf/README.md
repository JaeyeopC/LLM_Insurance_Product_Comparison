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

-  ```poetry install``` : install the dependencies
- ```poetry shell``` : activate the virtual environment
- ```poetry run kedro run``` : run the whole pipeline the order specified in ```__default__```  in ```pipeline_registry.py```
    - ```poetry run kedro run --node <node_name>``` : run the specific node
    - ```poetry run kedro run --pipeline <pipeline_name>``` : run the specific pipeline
    -  ```poetry run kedro run --pipeline <pipeline_name> --nodes <node_name>``` : run the specific node in the specific pipeline
- data pipeline names : ```pipeline_registry.py``` 
- input/output data : ```conf/base/catlog.yml``` and ```pipeline/nodes.py``` 
- supported data types : see [kedro_datasets](https://docs.kedro.org/projects/kedro-datasets/en/kedro-datasets-6.0.0/api/kedro_datasets.html) 
---------------------------------------
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
