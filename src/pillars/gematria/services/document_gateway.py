"""Document retrieval facade to keep UI free of persistence imports."""

from typing import Any

from shared.services.document_manager.document_service import document_service_context


def get_all_documents_metadata():
    """Return all document metadata records."""
    with document_service_context() as doc_service:
        return doc_service.get_all_documents_metadata()


def get_document(doc_id: Any):
    """Return a single document by id."""
    with document_service_context() as doc_service:
        return doc_service.get_document(doc_id)