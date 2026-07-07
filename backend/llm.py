import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

_llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME, temperature=0.3)

_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a cardiology assistant that helps interpret ECG classification results. "
            "Your role is to explain the result in a clear, concise, and medically accurate way. "
            "Always remind the patient that this is an AI-based analysis and not a substitute for professional medical advice."
        )
    ),
    (
        "human",
        (
            "The ECG classification model produced the following result:\n"
            "- Predicted class: {predicted_class} ({description})\n"
            "- Confidence: {confidence:.1%}\n"
            "- Class probabilities: {probabilities}\n\n"
            "Please provide a short, human-readable explanation of this result for the patient."
        )
    )
])

_chain = _prompt | _llm | StrOutputParser()


def explain_prediction(prediction: dict) -> str:
    """
    Takes a prediction result dict from model.py and returns
    a human-readable LLM explanation via Groq API.

    Expected keys: class, description, confidence, probabilities
    """
    probs_str = ", ".join(
        f"{cls}: {prob:.1%}" for cls, prob in prediction["probabilities"].items()
    )
    return _chain.invoke({
        "predicted_class": prediction["class"],
        "description": prediction["description"],
        "confidence": prediction["confidence"],
        "probabilities": probs_str,
    })
