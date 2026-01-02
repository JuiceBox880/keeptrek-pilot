# keeptrek-pilot
# KeepTrek Pilot

KeepTrek Pilot is a lightweight church‑metrics dashboard built with [Streamlit](https://streamlit.io/) and [Google Sheets](https://www.google.com/sheets/about/).  
It helps churches and community organizations track key participation metrics—attendance, new guests, and next‑step engagement—in one place.  
Data is stored in a Google Spreadsheet, and the dashboard provides an instant snapshot of totals, plus simple forms to add new entries.

## Features

- 📊 **Dashboard Overview** – View total attendance counts, number of new guests, and next‑step commitments at a glance.
- 📝 **Interactive Forms** – Add new attendance records, guest details, and next‑step commitments via intuitive Streamlit forms.
- 🧮 **Automatic Summaries** – The app sums attendance figures and counts guests/steps for you—no formulas required.
- 📁 **Google Sheets Backend** – Data is persisted in separate worksheet tabs (Attendance, New_Guests, Next_Steps) of your chosen Google Spreadsheet.
- 🎨 **Clean Styling** – Custom CSS gives the dashboard a polished look with gradient backgrounds and branded buttons.
- 🛠️ **Easily Extensible** – Built on a modular codebase with type hints, making it straightforward to adapt to other metrics.

## Prerequisites

- **Python 3.9+** – The app was developed against Python 3.10.
- **Google Cloud Service Account** – You'll need a service account JSON key with access to a Google Sheet where data will be stored.
- **Streamlit secrets configuration** – Store your service account JSON in Streamlit’s secrets management.

Clone the repository and install dependencies using `pip`:

```bash
git clone https://github.com/JuiceBox880/keeptrek-pilot.git
cd keeptrek-pilot
python -m venv .venv && source .venv/bin/activate  # optional but recommended
pip install -r requirements.txt
