
# African Voices: Annotator Audio Management Dashboard

A web-based backend system for managing, tracking, and analyzing annotated audio datasets across African languages (Yoruba, Igbo, Hausa, Pidgin). This platform is built to support voice data collection, monitoring annotator activity, and performing summary analytics in a structured and efficient way.

---

## 🌍 Project Objective

This project supports the development of large-scale voice datasets in underrepresented African languages. The backend enables administrators to track:
- Number of files submitted per language
- Annotator participation
- Duration of voice recordings
- Remaining unannotated texts
- Aggregated statistics for dashboard visualizations

---

## 📁 Project Structure

```
african_voices/
│
├── src/
│   ├── main.py                          # Entry point to the FastAPI application
│   ├── routes.py                        # All API route definitions
│   ├── models.py                        # Pydantic models for request/response validation
│   └── utils/
│       ├── audio_data_summary.py        # Summarizes audio dataset per language
│       ├── count_summary.py             # Computes count summaries of uploaded files
│       ├── hourly.py                    # Breakdown of submissions on an hourly basis
│       ├── audios_count.json            # Static JSON file for initial dataset count
│       ├── old_count.json               # Archived backup for previous counts
│       └── audio_data_summary_folder/
│           ├── audio_summary.py         # Core logic that computes the values seen in the dashboard
│           └── __pycache__/             # Python bytecode cache (excluded from versioning)
│
├── download_summary.py                  # Script to generate/download data summaries
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables (excluded from git)
├── .gitignore                           # Files and folders to ignore in Git
├── README.md                            # You are here :)
└── data/                                # (Optional) Folder for storing local test datasets
```

---

## ⚙️ Setup & Installation

> 💡 Python 3.10+ is required.

### 1. Clone the repository

```bash
git clone https://github.com/lawallanre00490038/african_voices.git
cd african_voices
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate     # On Linux/macOS
# OR
.venv\Scripts\activate        # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
# .env (example)
SECRET_KEY=your-secret-key
DEBUG=True
PORT=8000
```

---

## 🚀 Running the Application

```bash
uvicorn src.main:app --reload
```

Visit the app at: [http://localhost:8000](http://localhost:8000)  
View the interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📊 Example Output (from audio_summary.py)

Data generated from summaries:

| Language | Annotators | Files Read | Remaining Texts | Minutes Recorded | Hours Recorded |
|----------|------------|------------|------------------|------------------|----------------|
| Hausa    | 17         | 9,446      | -6,783           | 1,138.76         | 18.98          |
| Igbo     | 60         | 18,292     | 10,816           | 3,134.31         | 52.24          |
| Pidgin   | 372        | 107,754    | 99,635           | 14,498.48        | 241.64         |
| Yoruba   | 421        | 80,613     | 177,044          | 10,802.71        | 180.05         |

---

## 🧠 Summary of Key Files

| File                                         | Purpose                                                                 |
|----------------------------------------------|-------------------------------------------------------------------------|
| `main.py`                                    | Starts the FastAPI application                                          |
| `routes.py`                                  | Defines API endpoints (`/summary`, `/dashboard`, etc.)                  |
| `audio_data_summary.py`                      | Aggregates data and returns JSON-compatible statistics                  |
| `audio_summary.py`                           | Computes detailed stats per language                                   |
| `count_summary.py`                           | Calculates number of files per annotator/language                       |
| `hourly.py`                                  | Breaks down activities into hourly segments                             |
| `audios_count.json`, `old_count.json`        | Static input files used in data processing                              |
| `download_summary.py`                        | Downloads and exports analytics data                                    |

---

## 🔐 Security & Secrets

Your `.env` file is excluded from version control using `.gitignore`. **Never commit credentials.**

If GitHub blocks your push due to detected secrets, run:

```bash
git filter-repo --path .env --invert-paths
```

Then manually remove sensitive tokens or credentials from committed files.

---

## 🧼 Cleaning Large Files (Optional)

To remove accidentally committed large files (e.g., >50MB):

```bash
pip install git-filter-repo
git filter-repo --path <large-file> --invert-paths
```

---

## 👥 Contributing

1. Fork this repository
2. Create your feature branch:  
   `git checkout -b feature/your-feature`
3. Commit your changes:  
   `git commit -m 'Add some feature'`
4. Push to the branch:  
   `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for full license text.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Uvicorn](https://www.uvicorn.org/)
- [Data Science Nigeria (DSN)](https://www.datasciencenigeria.org/)
- The Open Source Community

---

## 👨🏽‍💻 Maintainer

**Lawal Olanrewaju**  
📧 [lawallanre49@gmail.com](mailto:lawallanre49@gmail.com)  
🔗 [GitHub Profile](https://github.com/lawallanre00490038)
