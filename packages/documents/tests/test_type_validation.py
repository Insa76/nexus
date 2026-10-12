from documents import (
    DocumentType,
    DocumentTypeValidation,
    DocumentTypeValidator,
)


def test_validation_reports_matching_types():
    validator = DocumentTypeValidator()

    result = validator.validate(
        declared_type="text/plain",
        detected_type=DocumentType.from_mime_type(
            "text/plain"
        ),
    )

    assert isinstance(
        result,
        DocumentTypeValidation,
    )
    assert result.matches
    assert not result.mismatch


def test_validation_reports_mismatching_types():
    validator = DocumentTypeValidator()

    result = validator.validate(
        declared_type="text/plain",
        detected_type=DocumentType.from_mime_type(
            "application/pdf"
        ),
    )

    assert not result.matches
    assert result.mismatch


def test_validation_accepts_document_type_as_declared_type():
    validator = DocumentTypeValidator()

    declared_type = DocumentType.from_mime_type(
        "text/plain"
    )

    result = validator.validate(
        declared_type=declared_type,
        detected_type=declared_type,
    )

    assert result.matches


def test_validation_normalizes_declared_mime_type():
    validator = DocumentTypeValidator()

    result = validator.validate(
        declared_type=" TEXT/PLAIN ",
        detected_type=DocumentType.from_mime_type(
            "text/plain"
        ),
    )

    assert result.matches


def test_validation_exposes_both_types():
    validator = DocumentTypeValidator()

    result = validator.validate(
        declared_type="text/plain",
        detected_type=DocumentType.from_mime_type(
            "application/pdf"
        ),
    )

    assert (
        result.declared_type.mime_type
        == "text/plain"
    )
    assert (
        result.detected_type.mime_type
        == "application/pdf"
    )
