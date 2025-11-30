
import pandas as pd
from transformers import pipeline
from sklearn.metrics import classification_report
import warnings
import torch

def test_language_detection(file_path: str):
    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

    try:
        df = pd.read_csv(file_path, lineterminator='\n')
        print(f"✅ Файл '{file_path}' успешно загружен. Всего записей для анализа: {len(df)}")
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл '{file_path}' не найден.")
        print("Пожалуйста, убедитесь, что файл 'language_dataset.csv' находится в папке 'data'.")
        return

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"\nИнициализация модели 'papluca/xlm-roberta-base-language-detection' на устройстве: {device.upper()}...")
    
    language_detector = pipeline(
        'text-classification',
        model='papluca/xlm-roberta-base-language-detection',
        device=device
    )

    texts = df['text'].astype(str).tolist()
    true_labels = df['expected_language'].astype(str).tolist()

    print(f"\n🚀 Запускаю определение языка для {len(texts)} текстов... Это может занять некоторое время.")
    
    predictions = language_detector(texts, batch_size=16, truncation=True)
    predicted_labels = [pred['label'] for pred in predictions]
    
    print("✅ Анализ завершен.")
    
    accuracy = sum(1 for pred, true in zip(predicted_labels, true_labels) if pred == true) / len(true_labels)

    print("\n------------------- РЕЗУЛЬТАТЫ -------------------")
    print(f"\n🎯 Средняя точность (Accuracy) по всему датасету: {accuracy:.2%}")

    print("\n📊 Детальный отчет по каждому языку:")
    class_labels = sorted(list(set(true_labels)))
    report = classification_report(true_labels, predicted_labels, labels=class_labels, zero_division=0)
    print(report)
    
    df['predicted_language'] = predicted_labels
    df['is_correct'] = (df['expected_language'] == df['predicted_language'])

    pd.set_option('display.max_colwidth', None)
    
    print("\n🔍 Первые 30 строк с результатами предсказаний:")
    print(df[['text', 'expected_language', 'predicted_language', 'is_correct']].head(30).to_string())

if __name__ == "__main__":
    DATA_FILE_PATH = "data/data.csv"
    test_language_detection(DATA_FILE_PATH)
