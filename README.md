# A Hybrid and ML-Enhanced FAQ Chatbot for XMUM Freshman Enquiries

This project develops a text-based FAQ chatbot prototype for XMUM freshman enquiries. The system combines rule-based intent detection, machine learning category classification, and retrieval-based answer matching.

## Main Features

- Categorized FAQ knowledge base
- Text preprocessing
- Rule-based intent detection
- ML category classification using TF-IDF and Logistic Regression
- Retrieval-based answer matching using cosine similarity
- Confidence-based response strategy
- Streamlit user interface

## Project Structure

- `data/`: FAQ datasets and training data
- `src/`: backend modules
- `models/`: trained classifier model
- `results/`: evaluation results and screenshots
- `docs/`: proposal, literature review, and final report
- `app.py`: Streamlit chatbot interface

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
