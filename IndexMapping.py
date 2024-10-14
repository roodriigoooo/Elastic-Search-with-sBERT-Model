mapping = {
    "properties":{
        "ProductID":{
        "type":"long"
    },
    
        "ProductName":{
        "type":"text"
    },
    
        "ProductBrand":{
        "type":"text"
    },
    
        "Gender":{
        "type":"text"
    },
    
        "Price":{
        "type":"long"
    },
    
        "NumImages":{
        "type":"long"
    },
    
        "PrimaryColor":{
        "type":"text"
    },
     
        "VectorDescription":{
        "type":"dense_vector",
        "dims":768,
        "index":True,
        "similarity": "cosine",
        "index_options": {
            "type":"hnsw", # approximate nearest neighbor for search speed, useful in larger datasets
            "m":16, # num of biirectional links.
            "ef_construction": 100 # recall during index construction
        }
    }
}

}

