"""
Error codes for Isopgem.

Centralized error codes make it easy to:
- Track which errors occur most frequently
- Provide consistent error messages
- Handle specific error cases
- Search logs for specific errors

Naming convention: {PILLAR}_{COMPONENT}_{ERROR_TYPE}
"""


class ErrorCode:
    """
    Centralized error codes.

    Each code is a unique identifier for a specific error condition.
    Use these instead of raw strings for consistency.
    """

    # ========================================================================
    # Generic / System Errors (ERR_SYS_*)
    # ========================================================================
    ERR_SYS_UNKNOWN = "ERR_SYS_UNKNOWN"
    ERR_SYS_OUT_OF_MEMORY = "ERR_SYS_OUT_OF_MEMORY"
    ERR_SYS_PERMISSION_DENIED = "ERR_SYS_PERMISSION_DENIED"
    ERR_SYS_DISK_FULL = "ERR_SYS_DISK_FULL"
    ERR_SYS_CONFIG_INVALID = "ERR_SYS_CONFIG_INVALID"

    # ========================================================================
    # File / Data Errors (ERR_DATA_*)
    # ========================================================================
    ERR_DATA_FILE_NOT_FOUND = "ERR_DATA_FILE_NOT_FOUND"
    ERR_DATA_FILE_CORRUPT = "ERR_DATA_FILE_CORRUPT"
    ERR_DATA_PARSE_ERROR = "ERR_DATA_PARSE_ERROR"
    ERR_DATA_WRITE_FAILED = "ERR_DATA_WRITE_FAILED"
    ERR_DATA_READ_FAILED = "ERR_DATA_READ_FAILED"

    # ========================================================================
    # Database Errors (ERR_DB_*)
    # ========================================================================
    ERR_DB_CONNECTION_FAILED = "ERR_DB_CONNECTION_FAILED"
    ERR_DB_QUERY_FAILED = "ERR_DB_QUERY_FAILED"
    ERR_DB_NOT_FOUND = "ERR_DB_NOT_FOUND"
    ERR_DB_CONSTRAINT_VIOLATION = "ERR_DB_CONSTRAINT_VIOLATION"
    ERR_DB_TRANSACTION_FAILED = "ERR_DB_TRANSACTION_FAILED"

    # ========================================================================
    # Lexicon Errors (ERR_LEX_*)
    # ========================================================================
    ERR_LEX_FILE_NOT_FOUND = "ERR_LEX_FILE_NOT_FOUND"
    ERR_LEX_PARSE_FAILED = "ERR_LEX_PARSE_FAILED"
    ERR_LEX_LOOKUP_FAILED = "ERR_LEX_LOOKUP_FAILED"
    ERR_LEX_NO_RESULTS = "ERR_LEX_NO_RESULTS"
    ERR_LEX_CACHE_FULL = "ERR_LEX_CACHE_FULL"
    ERR_LEX_INDEX_CORRUPT = "ERR_LEX_INDEX_CORRUPT"

    # ========================================================================
    # Etymology Errors (ERR_ETY_*)
    # ========================================================================
    ERR_ETY_DB_NOT_FOUND = "ERR_ETY_DB_NOT_FOUND"
    ERR_ETY_LOOKUP_FAILED = "ERR_ETY_LOOKUP_FAILED"
    ERR_ETY_API_FAILED = "ERR_ETY_API_FAILED"
    ERR_ETY_NETWORK_TIMEOUT = "ERR_ETY_NETWORK_TIMEOUT"

    # ========================================================================
    # Gematria Errors (ERR_GEM_*)
    # ========================================================================
    ERR_GEM_INVALID_INPUT = "ERR_GEM_INVALID_INPUT"
    ERR_GEM_CALCULATION_FAILED = "ERR_GEM_CALCULATION_FAILED"
    ERR_GEM_CIPHER_NOT_FOUND = "ERR_GEM_CIPHER_NOT_FOUND"
    ERR_GEM_NO_MAPPING = "ERR_GEM_NO_MAPPING"
    ERR_GEM_SAVE_FAILED = "ERR_GEM_SAVE_FAILED"

    # ========================================================================
    # Geometry Errors (ERR_GEO_*)
    # ========================================================================
    ERR_GEO_INVALID_DIMENSIONS = "ERR_GEO_INVALID_DIMENSIONS"
    ERR_GEO_CALCULATION_FAILED = "ERR_GEO_CALCULATION_FAILED"
    ERR_GEO_RENDER_FAILED = "ERR_GEO_RENDER_FAILED"

    # ========================================================================
    # Document Manager Errors (ERR_DOC_*)
    # ========================================================================
    ERR_DOC_NOT_FOUND = "ERR_DOC_NOT_FOUND"
    ERR_DOC_SAVE_FAILED = "ERR_DOC_SAVE_FAILED"
    ERR_DOC_LOAD_FAILED = "ERR_DOC_LOAD_FAILED"
    ERR_DOC_PARSE_FAILED = "ERR_DOC_PARSE_FAILED"
    ERR_DOC_EXPORT_FAILED = "ERR_DOC_EXPORT_FAILED"

    # ========================================================================
    # Astrology Errors (ERR_AST_*)
    # ========================================================================
    ERR_AST_EPHEMERIS_NOT_FOUND = "ERR_AST_EPHEMERIS_NOT_FOUND"
    ERR_AST_CALCULATION_FAILED = "ERR_AST_CALCULATION_FAILED"
    ERR_AST_INVALID_DATE = "ERR_AST_INVALID_DATE"
    ERR_AST_INVALID_LOCATION = "ERR_AST_INVALID_LOCATION"

    # ========================================================================
    # Network Errors (ERR_NET_*)
    # ========================================================================
    ERR_NET_CONNECTION_FAILED = "ERR_NET_CONNECTION_FAILED"
    ERR_NET_TIMEOUT = "ERR_NET_TIMEOUT"
    ERR_NET_API_ERROR = "ERR_NET_API_ERROR"
    ERR_NET_INVALID_RESPONSE = "ERR_NET_INVALID_RESPONSE"

    # ========================================================================
    # UI Errors (ERR_UI_*)
    # ========================================================================
    ERR_UI_RENDER_FAILED = "ERR_UI_RENDER_FAILED"
    ERR_UI_COMPONENT_NOT_FOUND = "ERR_UI_COMPONENT_NOT_FOUND"
    ERR_UI_INVALID_STATE = "ERR_UI_INVALID_STATE"

    # ========================================================================
    # Validation Errors (ERR_VAL_*)
    # ========================================================================
    ERR_VAL_REQUIRED_FIELD = "ERR_VAL_REQUIRED_FIELD"
    ERR_VAL_INVALID_FORMAT = "ERR_VAL_INVALID_FORMAT"
    ERR_VAL_OUT_OF_RANGE = "ERR_VAL_OUT_OF_RANGE"
    ERR_VAL_INVALID_TYPE = "ERR_VAL_INVALID_TYPE"


# User-friendly messages for each error code
ERROR_MESSAGES: dict[str, str] = {
    # System errors
    ErrorCode.ERR_SYS_UNKNOWN: "An unexpected error occurred",
    ErrorCode.ERR_SYS_OUT_OF_MEMORY: "The application is running out of memory",
    ErrorCode.ERR_SYS_PERMISSION_DENIED: "Permission denied to access this resource",
    ErrorCode.ERR_SYS_DISK_FULL: "Not enough disk space",
    ErrorCode.ERR_SYS_CONFIG_INVALID: "Invalid configuration",

    # Data errors
    ErrorCode.ERR_DATA_FILE_NOT_FOUND: "File not found",
    ErrorCode.ERR_DATA_FILE_CORRUPT: "File is corrupted or invalid",
    ErrorCode.ERR_DATA_PARSE_ERROR: "Failed to parse file",
    ErrorCode.ERR_DATA_WRITE_FAILED: "Failed to write to file",
    ErrorCode.ERR_DATA_READ_FAILED: "Failed to read from file",

    # Database errors
    ErrorCode.ERR_DB_CONNECTION_FAILED: "Failed to connect to database",
    ErrorCode.ERR_DB_QUERY_FAILED: "Database query failed",
    ErrorCode.ERR_DB_NOT_FOUND: "Record not found in database",
    ErrorCode.ERR_DB_CONSTRAINT_VIOLATION: "Database constraint violation",
    ErrorCode.ERR_DB_TRANSACTION_FAILED: "Database transaction failed",

    # Lexicon errors
    ErrorCode.ERR_LEX_FILE_NOT_FOUND: "Lexicon file not found",
    ErrorCode.ERR_LEX_PARSE_FAILED: "Failed to parse lexicon",
    ErrorCode.ERR_LEX_LOOKUP_FAILED: "Failed to look up word",
    ErrorCode.ERR_LEX_NO_RESULTS: "No lexicon results found",
    ErrorCode.ERR_LEX_CACHE_FULL: "Lexicon cache is full",
    ErrorCode.ERR_LEX_INDEX_CORRUPT: "Lexicon index is corrupted",

    # Etymology errors
    ErrorCode.ERR_ETY_DB_NOT_FOUND: "Etymology database not found",
    ErrorCode.ERR_ETY_LOOKUP_FAILED: "Failed to look up etymology",
    ErrorCode.ERR_ETY_API_FAILED: "Etymology API request failed",
    ErrorCode.ERR_ETY_NETWORK_TIMEOUT: "Network timeout while fetching etymology",

    # Gematria errors
    ErrorCode.ERR_GEM_INVALID_INPUT: "Invalid input for gematria calculation",
    ErrorCode.ERR_GEM_CALCULATION_FAILED: "Gematria calculation failed",
    ErrorCode.ERR_GEM_CIPHER_NOT_FOUND: "Cipher not found",
    ErrorCode.ERR_GEM_NO_MAPPING: "No mapping found for character",
    ErrorCode.ERR_GEM_SAVE_FAILED: "Failed to save calculation",

    # Geometry errors
    ErrorCode.ERR_GEO_INVALID_DIMENSIONS: "Invalid dimensions for geometry calculation",
    ErrorCode.ERR_GEO_CALCULATION_FAILED: "Geometry calculation failed",
    ErrorCode.ERR_GEO_RENDER_FAILED: "Failed to render geometry",

    # Document errors
    ErrorCode.ERR_DOC_NOT_FOUND: "Document not found",
    ErrorCode.ERR_DOC_SAVE_FAILED: "Failed to save document",
    ErrorCode.ERR_DOC_LOAD_FAILED: "Failed to load document",
    ErrorCode.ERR_DOC_PARSE_FAILED: "Failed to parse document",
    ErrorCode.ERR_DOC_EXPORT_FAILED: "Failed to export document",

    # Astrology errors
    ErrorCode.ERR_AST_EPHEMERIS_NOT_FOUND: "Ephemeris data not found",
    ErrorCode.ERR_AST_CALCULATION_FAILED: "Astrology calculation failed",
    ErrorCode.ERR_AST_INVALID_DATE: "Invalid date for astrology calculation",
    ErrorCode.ERR_AST_INVALID_LOCATION: "Invalid location coordinates",

    # Network errors
    ErrorCode.ERR_NET_CONNECTION_FAILED: "Failed to connect to server",
    ErrorCode.ERR_NET_TIMEOUT: "Network request timed out",
    ErrorCode.ERR_NET_API_ERROR: "API request failed",
    ErrorCode.ERR_NET_INVALID_RESPONSE: "Invalid response from server",

    # UI errors
    ErrorCode.ERR_UI_RENDER_FAILED: "Failed to render UI component",
    ErrorCode.ERR_UI_COMPONENT_NOT_FOUND: "UI component not found",
    ErrorCode.ERR_UI_INVALID_STATE: "Invalid UI state",

    # Validation errors
    ErrorCode.ERR_VAL_REQUIRED_FIELD: "Required field is missing",
    ErrorCode.ERR_VAL_INVALID_FORMAT: "Invalid format",
    ErrorCode.ERR_VAL_OUT_OF_RANGE: "Value is out of range",
    ErrorCode.ERR_VAL_INVALID_TYPE: "Invalid type",
}


def get_user_message(code: str) -> str:
    """Get user-friendly message for an error code."""
    return ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.ERR_SYS_UNKNOWN])
