# Database package for office-doc-agent
from .database_manager import DatabaseManager, get_database_manager
from .models import (
    AppSettings, DocumentRecord, PersonalTemplate, ProcessingResult,
    PerformanceRecord, BatchProcessingRecord,
    DocumentType, IntentType, ProcessingStatus, TemplateCategory, ResultType
)
from .repositories import (
    AppSettingsRepository,
    DocumentRepository,
    TemplateRepository,
    ProcessingResultRepository,
    PerformanceRepository,
    BatchProcessingRepository
)

__all__ = [
    'DatabaseManager',
    'get_database_manager',
    'AppSettings',
    'DocumentRecord',
    'PersonalTemplate',
    'ProcessingResult',
    'PerformanceRecord',
    'BatchProcessingRecord',
    'DocumentType',
    'IntentType',
    'ProcessingStatus',
    'TemplateCategory',
    'ResultType',
    'AppSettingsRepository',
    'DocumentRepository',
    'TemplateRepository',
    'ProcessingResultRepository',
    'PerformanceRepository',
    'BatchProcessingRepository'
]
