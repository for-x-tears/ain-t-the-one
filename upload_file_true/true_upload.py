from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

import polars as pl
from pydantic import BaseModel, Field, field_validator, ValidationError


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeedbackRecord(BaseModel):
    text: str = Field(..., min_length=1, description="Текст обращения")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    external_id: Optional[str] = Field(None, description="Внешний ID")
    timestamp: Optional[str] = Field(None, description="Время в ISO 8601")
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text не может быть пустой строкой")
        return v.strip()
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError):
            raise ValueError(f"Неверный формат timestamp: {v}")


class ValidationReport:
    
    def __init__(self):
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.invalid_rows: int = 0
        self.errors: List[Dict[str, Any]] = []
    
    def add_error(self, row_number: int, field: str, error: str, row_data: Dict):
        self.errors.append({
            "row_number": row_number,
            "field": field,
            "error": error,
            "row_data": row_data
        })
        self.invalid_rows += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "success_rate": f"{(self.valid_rows / self.total_rows * 100):.2f}%" if self.total_rows > 0 else "0%",
            "errors": self.errors
        }
    
    def print_summary(self):
        logger.info(f"Обработано строк: {self.total_rows}")
        logger.info(f"Валидных: {self.valid_rows}")
        logger.info(f"Невалидных: {self.invalid_rows}")
        if self.total_rows > 0:
            logger.info(f"Успешность: {(self.valid_rows / self.total_rows * 100):.2f}%")


class FileProcessor(ABC):
    
    def __init__(self, file_path: Path, chunk_size: int = 50000):
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.report = ValidationReport()
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    @abstractmethod
    def read_data(self) -> pl.DataFrame:
        pass
    
    def validate_structure(self, df: pl.DataFrame) -> bool:
        required_columns = {'text'}
        optional_columns = {'user_id', 'external_id', 'timestamp'}
        all_allowed_columns = required_columns | optional_columns
        
        df_columns = set(df.columns)
        
        missing_required = required_columns - df_columns
        if missing_required:
            raise ValueError(f"Отсутствуют обязательные столбцы: {missing_required}")
        
        extra_columns = df_columns - all_allowed_columns
        if extra_columns:
            logger.warning(f"Обнаружены дополнительные столбцы (будут проигнорированы): {extra_columns}")
            df = df.select([col for col in df.columns if col in all_allowed_columns])
        
        return True
    
    def validate_and_filter_records(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        valid_records = []
        
        records = df.to_dicts()
        self.report.total_rows = len(records)
        
        for idx, record in enumerate(records, start=1):
            try:
                record_data = {
                    'text': record.get('text'),
                    'user_id': record.get('user_id'),
                    'external_id': record.get('external_id'),
                    'timestamp': record.get('timestamp')
                }
                
                validated = FeedbackRecord(**record_data)
                
                result = validated.model_dump()
                if result['timestamp'] is None:
                    result['timestamp'] = datetime.now().isoformat()
                
                valid_records.append(result)
                self.report.valid_rows += 1
                
            except ValidationError as e:
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    self.report.add_error(
                        row_number=idx,
                        field=field,
                        error=error['msg'],
                        row_data=record
                    )
            except Exception as e:
                self.report.add_error(
                    row_number=idx,
                    field='unknown',
                    error=str(e),
                    row_data=record
                )
        
        return valid_records
    
    def process(self) -> Dict[str, Any]:
        logger.info(f"Начало обработки файла: {self.file_path}")
        
        try:
            df = self.read_data()
            logger.info(f"Прочитано строк: {len(df)}")
            
            self.validate_structure(df)
            logger.info("Структура файла валидна")
            
            valid_records = self.validate_and_filter_records(df)
            
            result = {
                "data": valid_records,
                "metadata": {
                    "source_file": str(self.file_path),
                    "processed_at": datetime.now().isoformat(),
                    "validation_report": self.report.to_dict()
                }
            }
            
            self.report.print_summary()
            logger.info("Обработка завершена успешно")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {e}")
            raise


class CSVProcessor(FileProcessor):
    
    def read_data(self) -> pl.DataFrame:
        try:
            df = pl.read_csv(
                self.file_path,
                separator=',',
                encoding='utf-8',
                null_values=['', 'NULL', 'null', 'None'],
                truncate_ragged_lines=True
            )
            return df
        except Exception as e:
            raise ValueError(f"Ошибка чтения CSV файла: {e}")


class ExcelProcessor(FileProcessor):
    
    def read_data(self) -> pl.DataFrame:
        try:
            df = pl.read_excel(
                self.file_path,
                sheet_id=1
            )
            return df
        except Exception as e:
            raise ValueError(f"Ошибка чтения Excel файла: {e}")


class JSONProcessor(FileProcessor):
    
    def read_data(self) -> pl.DataFrame:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                df = pl.read_ndjson(self.file_path)
            else:
                df = pl.DataFrame(data)
            
            return df
        except json.JSONDecodeError:
            try:
                df = pl.read_ndjson(self.file_path)
                return df
            except Exception as e:
                raise ValueError(f"Ошибка чтения JSON файла: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка чтения JSON файла: {e}")


class ParquetProcessor(FileProcessor):
    
    def read_data(self) -> pl.DataFrame:
        try:
            df = pl.read_parquet(self.file_path)
            return df
        except Exception as e:
            raise ValueError(f"Ошибка чтения Parquet файла: {e}")


class FileProcessorFactory:
    
    _processors = {
        '.csv': CSVProcessor,
        '.xlsx': ExcelProcessor,
        '.xls': ExcelProcessor,
        '.json': JSONProcessor,
        '.jsonl': JSONProcessor,
        '.parquet': ParquetProcessor
    }
    
    @classmethod
    def create_processor(cls, file_path: Path, chunk_size: int = 50000) -> FileProcessor:
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        processor_class = cls._processors.get(extension)
        if processor_class is None:
            raise ValueError(
                f"Неподдерживаемый формат файла: {extension}. "
                f"Поддерживаются: {list(cls._processors.keys())}"
            )
        
        return processor_class(file_path, chunk_size)


def find_file_in_directory(directory: str) -> Optional[Path]:
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Директория не найдена: {directory}")
    
    if not dir_path.is_dir():
        raise ValueError(f"Путь не является директорией: {directory}")
    
    supported_extensions = ['.csv', '.xlsx', '.xls', '.json', '.jsonl', '.parquet']
    
    for ext in supported_extensions:
        files = list(dir_path.glob(f'*{ext}'))
        if files:
            logger.info(f"Найден файл: {files[0]}")
            return files[0]
    
    return None


def process_file(file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    path = Path(file_path)
    
    if path.is_dir():
        found_file = find_file_in_directory(file_path)
        if found_file is None:
            raise FileNotFoundError(
                f"В директории {file_path} не найдено файлов поддерживаемых форматов "
                f"(csv, xlsx, xls, json, jsonl, parquet)"
            )
        file_path = found_file
    
    processor = FileProcessorFactory.create_processor(file_path)
    
    result = processor.process()
    
    if output_path:
        output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Результат сохранен в: {output_path}")
    
    return result

if __name__ == "__main__":
    input_file = "file/"
    output_file = "file/result.json"
    
    try:
        result = process_file(input_file, output_file)
        print(f"\nОбработано записей: {len(result['data'])}")
        print(f"Отчет о валидации: {result['metadata']['validation_report']}")
    except Exception as e:
        print(f"Ошибка: {e}")