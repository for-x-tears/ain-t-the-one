
import pandas as pd
from transformers import pipeline
from sklearn.metrics import classification_report
import warnings
import torch

def normalize_sentiment_label(label: str) -> str:
    """
    Приводит гранулярные метки ('very positive', 'very negative')
    к трем основным классам ('positive', 'negative', 'neutral').
    """
    label_lower = label.lower()
    if 'positive' in label_lower:
        return 'positive'
    if 'negative' in label_lower:
        return 'negative'
    return 'neutral'

def analyze_sentiment(file_path: str):
    """
    Основная функция для анализа сентимента из CSV-файла.

    Args:
        file_path (str): Путь к CSV-файлу с данными.
    """
    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

    try:
        df = pd.read_csv(file_path)
        print(f"✅ Файл '{file_path}' успешно загружен. Всего записей для анализа: {len(df)}")
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл '{file_path}' не найден.")
        print("Пожалуйста, убедитесь, что файл находится в папке 'data'.")
        return

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"\nИнициализация модели 'tabularai/multilingual-sentiment-analysis' на устройстве: {device.upper()}...")
    
    sentiment_analyzer = pipeline(
        'sentiment-analysis',
        model='tabularisai/multilingual-sentiment-analysis',
        device=device
    )

    texts = df['Review'].tolist()
    true_labels = df['Sentiment'].tolist()

    print(f"\n🚀 Запускаю анализ сентимента для {len(texts)} текстов... Это может занять некоторое время на CPU.")
    
    predictions_raw = sentiment_analyzer(texts, batch_size=16, truncation=True)
    
    print("✅ Анализ завершен.")

    predicted_labels = [normalize_sentiment_label(pred['label']) for pred in predictions_raw]
    true_labels_lower = [str(label).lower() for label in true_labels]
    
    accuracy = sum(1 for pred, true in zip(predicted_labels, true_labels_lower) if pred == true) / len(true_labels_lower)

    print("\n------------------- РЕЗУЛЬТАТЫ -------------------")
    print(f"\n🎯 Средняя точность (Accuracy) по всему датасету: {accuracy:.2%}")

    print("\n📊 Детальный отчет по каждому классу:")
    class_labels = sorted(list(set(true_labels_lower)))
    report = classification_report(true_labels_lower, predicted_labels, labels=class_labels, zero_division=0)
    print(report)
    

    df['predicted_sentiment'] = predicted_labels
    df['is_correct'] = (df['Sentiment'].str.lower() == df['predicted_sentiment'])

    pd.set_option('display.max_colwidth', None)
    
    print("\n🔍 Первые 30 строк с результатами предсказаний:")
    print(df[['message_text', 'expected_sentiment', 'predicted_sentiment', 'is_correct']].head(30).to_string())


if __name__ == "__main__":
    DATA_FILE_PATH = "data/dataset.csv"
    analyze_sentiment(DATA_FILE_PATH)