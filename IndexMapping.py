mapping = {
    "properties":{
        "ProductID": {"type": "long"},
        "ProductName": {"type": "text"},
        "ProductBrand": {"type": "keyword"},
        "Gender": {"type": "keyword"},
        "Price": {"type": "float"},
        "NumImages": {"type": "integer"},
        "PrimaryColor": {"type": "keyword"},
        "VectorDescription": {
            "type": "dense_vector",
            "dims": 768,
            "index": True,
            "similarity": "cosine",
            "index_options": {
                "type": "hnsw",  # approximate nearest neighbor for search speed, useful in larger datasets
                "m": 16,  # num of biirectional links.
                "ef_construction": 100  # recall during index construction
            }
        },
        "Description": {"type": "text"}
    }
}

# Changed some features to keyword type to support exact match filtering and aggregations.
# I also changed Price to float to support numeric range queries.

