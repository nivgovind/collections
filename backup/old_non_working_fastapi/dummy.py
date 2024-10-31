from utils.s3_utils import check_connection, list_documents, get_document_details

print("Checking S3 connection...")
print(check_connection())

print("Listing documents...")
print(list_documents())

document_name = 'example_document.txt'
print(f"Getting details for document: {document_name}")
print(get_document_details(document_name))