from documents.models import Document
from documents.store import DocumentStore


def test_list_for_user_returns_only_documents_for_user():
    store = DocumentStore()

    user_a_document = Document.create(
        name="Documento A",
        mime_type="text/plain",
        source="a.txt",
        user_id="user-a",
    )

    user_b_document = Document.create(
        name="Documento B",
        mime_type="text/plain",
        source="b.txt",
        user_id="user-b",
    )

    user_a_second_document = Document.create(
        name="Documento C",
        mime_type="text/plain",
        source="c.txt",
        user_id="user-a",
    )

    store.add(user_a_document)
    store.add(user_b_document)
    store.add(user_a_second_document)

    result = store.list_for_user("user-a")

    assert result == [
        user_a_document,
        user_a_second_document,
    ]


def test_list_for_user_returns_empty_list_when_user_has_no_documents():
    store = DocumentStore()

    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    store.add(document)

    assert store.list_for_user("user-b") == []


def test_list_for_user_does_not_include_documents_without_user():
    store = DocumentStore()

    document_without_user = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    store.add(document_without_user)

    assert store.list_for_user("user-a") == []

def test_list_for_organization_returns_only_documents_for_organization():
    store = DocumentStore()

    organization_a_document = Document.create(
        name="Documento A",
        mime_type="text/plain",
        source="a.txt",
        organization_id="organization-a",
    )

    organization_b_document = Document.create(
        name="Documento B",
        mime_type="text/plain",
        source="b.txt",
        organization_id="organization-b",
    )

    organization_a_second_document = Document.create(
        name="Documento C",
        mime_type="text/plain",
        source="c.txt",
        organization_id="organization-a",
    )

    store.add(organization_a_document)
    store.add(organization_b_document)
    store.add(organization_a_second_document)

    result = store.list_for_organization("organization-a")

    assert result == [
        organization_a_document,
        organization_a_second_document,
    ]


def test_list_for_organization_returns_empty_list_when_organization_has_no_documents():
    store = DocumentStore()

    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        organization_id="organization-a",
    )

    store.add(document)

    assert store.list_for_organization("organization-b") == []


def test_list_for_organization_does_not_include_documents_without_organization():
    store = DocumentStore()

    document_without_organization = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    store.add(document_without_organization)

    assert store.list_for_organization("organization-a") == []

def test_list_for_project_returns_only_documents_for_project():
    store = DocumentStore()

    project_a_document = Document.create(
        name="Documento A",
        mime_type="text/plain",
        source="a.txt",
        project_id="project-a",
    )

    project_b_document = Document.create(
        name="Documento B",
        mime_type="text/plain",
        source="b.txt",
        project_id="project-b",
    )

    project_a_second_document = Document.create(
        name="Documento C",
        mime_type="text/plain",
        source="c.txt",
        project_id="project-a",
    )

    store.add(project_a_document)
    store.add(project_b_document)
    store.add(project_a_second_document)

    result = store.list_for_project("project-a")

    assert result == [
        project_a_document,
        project_a_second_document,
    ]


def test_list_for_project_returns_empty_list_when_project_has_no_documents():
    store = DocumentStore()

    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        project_id="project-a",
    )

    store.add(document)

    assert store.list_for_project("project-b") == []


def test_list_for_project_does_not_include_documents_without_project():
    store = DocumentStore()

    document_without_project = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    store.add(document_without_project)

    assert store.list_for_project("project-a") == []

def test_list_for_context_filters_by_user():
    store = DocumentStore()

    matching = Document.create(
        name="Matching",
        mime_type="text/plain",
        source="matching.txt",
        user_id="user-a",
    )

    other_user = Document.create(
        name="Other User",
        mime_type="text/plain",
        source="other-user.txt",
        user_id="user-b",
    )

    store.add(matching)
    store.add(other_user)

    assert store.list_for_context(
        user_id="user-a",
    ) == [matching]


def test_list_for_context_filters_by_organization():
    store = DocumentStore()

    matching = Document.create(
        name="Matching",
        mime_type="text/plain",
        source="matching.txt",
        organization_id="organization-a",
    )

    other_organization = Document.create(
        name="Other Organization",
        mime_type="text/plain",
        source="other.txt",
        organization_id="organization-b",
    )

    store.add(matching)
    store.add(other_organization)

    assert store.list_for_context(
        organization_id="organization-a",
    ) == [matching]


def test_list_for_context_filters_by_project():
    store = DocumentStore()

    matching = Document.create(
        name="Matching",
        mime_type="text/plain",
        source="matching.txt",
        project_id="project-a",
    )

    other_project = Document.create(
        name="Other Project",
        mime_type="text/plain",
        source="other.txt",
        project_id="project-b",
    )

    store.add(matching)
    store.add(other_project)

    assert store.list_for_context(
        project_id="project-a",
    ) == [matching]


def test_list_for_context_combines_context_filters():
    store = DocumentStore()

    matching = Document.create(
        name="Matching",
        mime_type="text/plain",
        source="matching.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    wrong_user = Document.create(
        name="Wrong User",
        mime_type="text/plain",
        source="wrong-user.txt",
        user_id="user-b",
        organization_id="organization-a",
        project_id="project-a",
    )

    wrong_organization = Document.create(
        name="Wrong Organization",
        mime_type="text/plain",
        source="wrong-organization.txt",
        user_id="user-a",
        organization_id="organization-b",
        project_id="project-a",
    )

    wrong_project = Document.create(
        name="Wrong Project",
        mime_type="text/plain",
        source="wrong-project.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-b",
    )

    store.add(matching)
    store.add(wrong_user)
    store.add(wrong_organization)
    store.add(wrong_project)

    assert store.list_for_context(
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    ) == [matching]


def test_list_for_context_requires_at_least_one_filter():
    store = DocumentStore()

    try:
        store.list_for_context()
    except ValueError as exc:
        assert str(exc) == (
            "At least one document context filter is required"
        )
    else:
        raise AssertionError(
            "Expected ValueError when no context filter is provided"
        )
