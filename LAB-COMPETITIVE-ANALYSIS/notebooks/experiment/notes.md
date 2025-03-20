
# **Notes for the Experiment Pipeline**

---

## **1. Crawling Pipeline**
- We need to create a `.txt` list of the insurance companies we need to crawl and automate crawling based on this list.
- Consider focusing on **US or UK companies** (for the first prototype) since applying classical NLP approaches in **German** introduces extra work:
  - Example: 
    ```
    sklearn.utils._param_validation.InvalidParameterError: The 'stop_words' parameter of TfidfVectorizer must be a str among {'english'}, an instance of 'list' or None. Got 'german' instead.
    ```
- **TODO:** Increase the depth of crawling (to include more insurance products and features) and expand the number of companies (from 3 to 10).
- Optional but beneficial:
  - Since many pages lack insurance product information and classification could take time:
    - Explore **AI-based crawling methods** OR
    - Apply filters on the **HTML page title** to check if it includes keywords like "product."

---

## **2. HTML to JSON Pipeline**
- Instead of `.txt`, convert HTML to JSON while preserving necessary content, ensuring a sample structure like:

  ```json
  {
    "company_name": "axa_germany",
    "pages": [
        {
            "company_name": "axa_germany",
            "title": "FAQ rund um deine Bewerbung / Karriere bei AXA",
            "page_name": "karriere_bewerbung-faq",
            "refined_text": "HomeKarriereFAQ rund um deine Bewerbung![Häufige Fragen FAQ | AXA]()...",
            "subtitles": [],
            "tables": []
        }
    ]
  }
  ```

- **Metadata Selection:** Decide which metadata to use for **context extraction**:
  - Example: Use only **title data** for product classification instead of full content to avoid dependency on LLMs.

---

## **3. Create Reference Table for Products, Features, and Content-Answering Questions**
- Create a reference table with:
  - **20 most common products.**
  - **10 common features per product.**
  - **3-4 feature-specific questions.**

### **Example Reference Data**:

```json
{
    "product_name": "Health Insurance (Gesetzliche Krankenversicherung)",
    "features": [
        {
            "feature_name": "Comprehensive Medical Coverage",
            "feature_questions": [
                "What medical services are included in the Comprehensive Medical Coverage?",
                "Are there any limitations or exclusions in the Comprehensive Medical Coverage?",
                "Does it cover pre-existing conditions?",
                "How does it handle emergency medical situations?"
            ]
        },
        {
            "feature_name": "Prescription Drug Coverage",
            "feature_questions": [
                "What types of prescription drugs are covered?",
                "Are there any limitations or exclusions?",
                "Does this feature require co-payments or deductibles?",
                "What are the procedures to claim this coverage?"
            ]
        }
    ]
}
```

- **TODO:** Refine LLM prompting to improve and generalize reference data generation.

---

## **4. Classify Products Based on JSON Titles**
- Use **semantic similarity** to match reference product names with JSON titles and create a database:
  ```
  {company_name}/{product_name}.json
  ```
- This ensures feature content extraction is focused only on the relevant `{product_name}.json` file.
- **TODO:** Develop a method to minimize information loss caused by semantic similarity limitations.
  - Alternative: Use **content summaries** combined with reference insurance products.

---

## **5. Extract Product Feature Information**
- Extract feature details based on the **questions in the reference table.**

---

## **6. Create a Product Feature Matrix**
- Compile extracted information into a structured **feature matrix** for further analysis.

---

# **What We Can Do More**
- **Create an Asana Board:**
  - Break tasks into smaller, more manageable steps for better control.
- **Documentation:** 
  - Write short, concise documentation for each task to enable team collaboration.
- **Task Splitting:**
  - Assign tasks such that different people handle distinct sections to avoid overlap.
