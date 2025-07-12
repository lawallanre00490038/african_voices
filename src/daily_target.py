from datetime import datetime, timedelta
import math
import pandas as pd

# Define targets and today's completed hours
targets = {
    "Pidgin": {"target_hours": 1000, "today_hours": 178.79},
    "Yoruba": {"target_hours": 500, "today_hours": 94.57},
    "Igbo": {"target_hours": 500, "today_hours": 45.68}
}

# Constants
sentence_duration_secs = 8
sentences_per_annotator_per_day = 200  # Updated from 600 to 500
start_date = datetime(2025, 7, 3)
end_date = datetime(2025, 7, 7)
days = (end_date - start_date).days + 1

# Forecast
for language, data in targets.items():
    total_target_hours = data["target_hours"]
    start_hours = data["today_hours"]
    remaining_hours = total_target_hours - start_hours

    # Staggered distribution weights
    daily_growth = [1.0 + 0.2 * i for i in range(days)]
    total_growth = sum(daily_growth)
    scaled_daily_hours = [(g / total_growth) * remaining_hours for g in daily_growth]

    cumulative_hours = []
    cumulative_sentences = []
    cumulative_annotators = []

    cum_hours = start_hours
    for h in scaled_daily_hours:
        cum_hours += h
        cumulative_hours.append(round(cum_hours, 2))
        total_seconds = cum_hours * 3600
        total_sentences = int(total_seconds / sentence_duration_secs)
        cumulative_sentences.append(total_sentences)
        cumulative_annotators.append(math.ceil(total_sentences / sentences_per_annotator_per_day))

    # Compute deltas
    delta_hours = ["-"] + [round(cumulative_hours[i] - cumulative_hours[i-1], 2) for i in range(1, days)]
    delta_sentences = ["-"] + [cumulative_sentences[i] - cumulative_sentences[i-1] for i in range(1, days)]
    delta_annotators = ["-"] + [cumulative_annotators[i] - cumulative_annotators[i-1] for i in range(1, days)]

    # Assemble DataFrame
    df = pd.DataFrame({
        "Date": [(start_date + timedelta(days=i)).strftime("%b %d") for i in range(days)],
        "Target Hours": cumulative_hours,
        "+Δ Hours": delta_hours,
        "Target Sentences": cumulative_sentences,
        "+Δ Sentences": delta_sentences,
        "Est. number of annotators (Voice 200 sentences/day)": cumulative_annotators,
        "+Δ Annotators": delta_annotators
    })

    # Output
    print(f"\n📊 Forecast for {language}:\n")
    print(df.to_string(index=False))
