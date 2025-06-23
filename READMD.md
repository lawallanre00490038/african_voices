# ----------- STEP 4: How to Run -----------
# Clone your repo locally in the project folder:
#
65750bc763851039bd4bf3c48f46c484141f0c0a9b79cdbb9e55c7c611aa6952
 git clone git@github.com:your-org/language-data.git data_repo

# Then run the server:
# uvicorn webhook_server:app --host 0.0.0.0 --port 8000

# Expose with Ngrok (optional):
# ngrok http 8000

yeah
https://console.cron-job.org/dashboard



alembic init alembic
# Edit env.py to use SQLModel metadata
alembic revision --autogenerate -m "create annotator stats table"
alembic upgrade head



✅ 2. Open Power BI Desktop
🔁 Method: Connect via Web → JSON API
Go to Power BI Desktop

Click on Home → Get Data → Web

Choose Advanced

In URL parts, enter:

bash
Copy
Edit
http://localhost:8000/annotators
