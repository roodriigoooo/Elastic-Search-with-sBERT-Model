import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


indexName = "all_products"

USERNAME_AUTH="junior"
PASSWORD_AUTH="**********"
try:
    es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(USERNAME_AUTH, PASSWORD_AUTH),
    #verify_certs=False 
)
except ConnectionError as e:
    print("Connection Error:", e)
    
if es.ping():
    print("Succesfully connected to ElasticSearch!!")
else:
    print("Can not connect to Elasticsearch!")


def search(input_keyword):
    model = SentenceTransformer('all-mpnet-base-v2') #load fine-tuned model
    vector_of_input_keyword = model.encode(input_keyword)

    query = {
        "size":5,
        "query": {
            "function_score": {
                "query": {
                    "multi_match": { # keyword search on specified fields
                        "query": input_keyword,
                        "fields": ["ProductName^2", "ProductBrand", "PrimaryColor"]
                    }
                }
                "functions":[
                    {
                        "script_score": { # calculates similarity score between query vector and doc vectors.
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'VectorDescription') + 1.0",
                                "params": {
                                    "query_vector": vector_of_input_keyword
                                }
                            }
                        }
                    }
                ],
                "boost_mode": "sum", # combine original query score and function score
                "score_mode": "sum"
            }
        },
        "_source": ["ProductName", "Description"]
    }

    res = es.search(index="clothing", body=query)
    results = res["hits"]["hits"]

    return results

def main():
    st.title("Helpful Engineering Organization")

    # Input: User enters search query
    search_query = st.text_input("Enter your search query")

    # Button: User triggers the search
    if st.button("Search"):
        if search_query:
            # Perform the search and get results
            results = search(search_query)

            # Display search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if '_source' in result:
                        try:
                            st.header(f"{result['_source']['ProductName']}")
                        except Exception as e:
                            print(e)
                        
                        try:
                            st.write(f"Description: {result['_source']['Description']}")
                        except Exception as e:
                            print(e)
                        st.divider()

                    
if __name__ == "__main__":
    main()
