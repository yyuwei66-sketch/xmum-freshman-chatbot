# A Hybrid and ML-Enhanced FAQ Chatbot for XMUM Freshman Enquiries

This project develops a text-based FAQ chatbot prototype for XMUM freshman enquiries. The system combines rule-based intent detection, machine learning category classification, and retrieval-based answer matching.

## Main Features

- Categorized FAQ knowledge base
- Text preprocessing
- Rule-based intent detection
- ML category classification using Naive Bayes (best performing) and Linear SVM
- Retrieval-based answer matching using cosine similarity
- Confidence-based response strategy
- Flask web interface using the design in `ui/`

## Project Structure

- `data/`: FAQ datasets and training data
- `src/`: backend modules
- `models/`: trained classifier model
- `results/`: evaluation results and screenshots
- `docs/`: proposal, literature review, and final report
- `app.py`: Flask web server and chatbot API
- `ui/`: browser interface

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Model & Run Comparison (Optional)
If you want to retrain the ML classifier and generate the comparison reports, run:
```bash
python -c "import sys; sys.path.insert(0,'src'); import classifier; classifier.train_and_compare()"
```
*The evaluation results will be saved to the `results/` folder.*

### 3. Run Unit Tests
To verify that the classifier logic works correctly, run:
```bash
pytest tests/ -v
```

### 4. Start the Chatbot UI
```bash
python app.py
```

Then open `http://127.0.0.1:5000`. The retrieval model is loaded when the
server starts, so startup may take a moment. To expose the app on a trusted
local network, run `flask --app app run --host 0.0.0.0`.
