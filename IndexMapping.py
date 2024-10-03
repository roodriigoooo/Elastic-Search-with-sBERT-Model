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
        "similarity": "l2_norm"
    }
}

}

