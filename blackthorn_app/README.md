# Blackthorn: independent cyber risk rating (prototype app)

## Files
- `assumptions.py`: every number the model uses, with its source. **Update data here.**
- `model.py`: the calculations (same model as notebook version 4).
- `app.py`: the web page (questionnaire, rating card, next steps, charts).
- `visuals.py`: icons, animated charts and the animation styles.
- `requirements.txt`: the Python packages needed.
- `assets/`: Blackthorn logo, seal, favicon and brand font.
- `.streamlit/config.toml`: the dark Blackthorn colour theme.

## Run it on your laptop
1. Install Python 3 from python.org (tick "Add Python to PATH" on Windows).
2. Open a terminal in this folder and run:
   pip install -r requirements.txt
3. Then run:
   streamlit run app.py
4. A browser tab opens. Fill in the questions on the left and click "Calculate my rating".

## Put it online (free)
1. Make a free GitHub account and upload these four files to a new repository.
2. Go to share.streamlit.io, sign in with GitHub, choose the repository and `app.py`, and click Deploy.
3. You get a link you can send to anyone.

## Updating the data
Open `assumptions.py`, change the numbers (each one is labelled REAL, ASSUMPTION or PLACEHOLDER),
save, and refresh the app. Nothing else needs to change.

## Privacy
The app doesn't save anything anyone enters. Keep it that way until there's a privacy notice in place.
