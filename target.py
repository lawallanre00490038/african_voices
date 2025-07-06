# import math
# import pandas as pd

# # Configuration
# sentence_duration_sec = 8
# sentences_per_minute = 60 / sentence_duration_sec
# sentences_per_hour = sentences_per_minute * 60

# # Targets
# targets = {
#     "Pidgin": {"target_hours": 1000, "today_hours": 152.98},
#     "Yoruba": {"target_hours": 500, "today_hours": 78.83},
#     "Igbo": {"target_hours": 500, "today_hours": 42.29}
# }

# # Forecast days
# days = ["July 2", "July 3", "July 4", "July 5", "July 6", "July 7"]

# def stagger_plan(total_hours, stages):
#     """
#     Spread hours over days in a growing manner.
#     """
#     # Normalize pattern to match total_hours
#     weights = [60, 90, 120, 150, 170, 200]
#     total_weight = sum(weights[:stages])
#     return [round(h / total_weight * total_hours, 2) for h in weights[:stages]]

# forecast = {}

# for lang, data in targets.items():
#     remaining_hours = round(data["target_hours"] - data["today_hours"], 2)
#     remaining_sentences = round(remaining_hours * sentences_per_hour)

#     daily_hours = stagger_plan(remaining_hours, len(days))

#     daily_sentences = [round(h * sentences_per_hour) for h in daily_hours]
#     daily_annotators = [math.ceil(s / 600) for s in daily_sentences]

#     forecast[lang] = pd.DataFrame({
#         "Date": days,
#         "Target Hours": daily_hours,
#         "Target Sentences": daily_sentences,
#         "Est. Annotators (600 sent/day)": daily_annotators
#     })

# # Output
# for lang, df in forecast.items():
#     print(f"\n📊 Forecast for {lang}:\n")
#     print(df.to_string(index=False))

# print("\n\n\n")






# from datetime import datetime, timedelta
# import math
# import pandas as pd

# # Define targets and today's completed hours
# targets = {
#     "Pidgin": {"target_hours": 1000, "today_hours": 152.98},
#     "Yoruba": {"target_hours": 500, "today_hours": 78.83},
#     "Igbo": {"target_hours": 500, "today_hours": 42.29}
# }

# # Constants
# sentence_duration_secs = 8
# sentences_per_annotator_per_day = 500
# start_date = datetime(2025, 7, 2)
# end_date = datetime(2025, 7, 7)
# days = (end_date - start_date).days + 1

# # Prepare forecast for each language
# forecast_results = {}

# for language, data in targets.items():
#     total_target_hours = data["target_hours"]
#     start_hours = data["today_hours"]
#     remaining_hours = total_target_hours - start_hours

#     # Simulate a staggered growth pattern
#     daily_growth = [1.0 + 0.2 * i for i in range(days)]
#     total_growth = sum(daily_growth)
#     scaled_targets = [(g / total_growth) * remaining_hours for g in daily_growth]

#     cumulative_hours = start_hours
#     forecast = []

#     for i in range(days):
#         date = (start_date + timedelta(days=i)).strftime("%b %d")
#         daily_hours = scaled_targets[i]
#         cumulative_hours += daily_hours
#         target_sentences = int((cumulative_hours * 3600) / sentence_duration_secs)
#         est_annotators = math.ceil(target_sentences / sentences_per_annotator_per_day)

#         forecast.append({
#             "Date": date,
#             "Target Hours": round(cumulative_hours, 2),
#             "Target Sentences": target_sentences,
#             "Est. Annotators (500 sent/day)": est_annotators
#         })

#     df = pd.DataFrame(forecast)
#     print(f"\nForecast for {language}:\n")
#     print(df.to_string(index=False))





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
