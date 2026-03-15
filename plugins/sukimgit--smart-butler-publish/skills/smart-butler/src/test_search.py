from doc_search import search_documents

results = search_documents('人员密集度', 'D:\\OpenClawDocs', 5)
print(f'Found: {len(results)} documents\n')
for i, r in enumerate(results, 1):
    print(f'{i+1}. {r["filename"]}')
    print(f'   Path: {r["path"]}')
    print()
