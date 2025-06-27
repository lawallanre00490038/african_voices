from src.utils.audio_data_summary import fetch_excel_from_github





if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/lawallanre00490038/dsn-voice/main/reports/audio_data_summary.xlsx"
    file = fetch_excel_from_github(url)
    print(file.sheet_names)