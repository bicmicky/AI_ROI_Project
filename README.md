# AI_ROI_Project

This is a test project to estimate the ROI of AI projects. 
This is my first Streamlit app, so please be gentle with your feedback. 
I welcome any suggestions for improvements.

## AI ROI Calculator

Small Streamlit app for estimating the return on an AI initiative.

## What it does

- Estimates labor savings from time saved
- Adds optional revenue uplift and manual-cost reduction
- Calculates first-year ROI, payback period, and break-even timing
- Shows a 12-month cash-flow view
- Saves scenarios in a local SQLite database

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` - Streamlit UI
- `roi_model.py` - ROI calculation logic
- `roi_db.py` - SQLite storage helpers
- `requirements.txt` - Python dependencies
