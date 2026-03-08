# services/query_processor.py

from services.llm_extractor import llm_extract
from services.dataset_router import detect_dataset
from services.analytics_engine import run_analysis
from services.insight_generator import generate_insight


def process_query(user_query):

    # 1. Extract intent using LLM
    intent_data = llm_extract(user_query)

    if not intent_data:
        return {"answer": "Sorry, I couldn't understand the query."}

    # 2. Detect dataset
    dataset = detect_dataset(intent_data)

    if not dataset:
        return {"answer": "Dataset not found for this query."}

    # 3. Run analytics
    result = run_analysis(intent_data, dataset)

    if result is None:
        return {"answer": "Unable to process request."}

    # 4. Generate insight
    insight = generate_insight(intent_data, result)

    return {
        "data": result,
        "answer": insight
    }