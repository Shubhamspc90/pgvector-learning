-- Prevent duplicate documents from being inserted

ALTER TABLE semantic_documents
ADD CONSTRAINT unique_semantic_document_content
UNIQUE (content);