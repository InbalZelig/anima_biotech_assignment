# anima_biotech_assignment

Provide a viewer app for biologists to analyze the output of IMV (image validation).
All images from microscopy scan in the company undergo a QA procedure by a Python 
script named IMV (for Image Validation). The result of IMV is a csv file that stores 
quality measurements in tabular form.

The app is based on Streamlit framework.

Prerequisite:
- streamlit
- altair
- streamlit_vega_lite

Run the app:
`streamlit run image_validation_app.py`