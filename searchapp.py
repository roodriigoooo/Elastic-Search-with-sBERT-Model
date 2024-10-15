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

@st.cache_resource
def load_model():
    return SentenceTransformer('all-mpnet-base-v2')


model = load_model()


def search(input_keyword, selected_filters):
    vector_of_input_keyword = model.encode(input_keyword).tolist()

    query = {
        "size": 10,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": input_keyword,
                                    "fields": ["ProductName^2", "ProductBrand", "PrimaryColor"]
                                }
                            },
                            {
                                "script_score": {
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'VectorDescription') + 1.0",
                                        "params": {
                                            "query_vector": vector_of_input_keyword
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                "boost_mode": "sum",
                "score_mode": "sum"
            }
        },
        "_source": ["ProductName", "Description", "ProductBrand", "Price", "PrimaryColor", "Gender"],
        "aggs": {
            "ProductBrand": {
                "terms": {"field": "ProductBrand"}
            },
            "PrimaryColor": {
                "terms": {"field": "PrimaryColor"}
            },
            "Gender": {
                "terms": {"field": "PrimaryColor"}
            },
            "PriceRange": {
                "range": {
                    "field": "Price",
                    "ranges": [
                        {"to": 1000, "key": "Under 1000"},
                        {"from": 1000, "to": 5000, "key": "1000-5000"},
                        {"from": 5000, "key": "Over 5000"}
                    ]
                }
            }
        }
    }
    # Apply filters based on selected facets
    if selected_filters:
        filter_clauses = []
        for field, values in selected_filters.items():
            if field == "Price":
                # Handle price range filters
                range_filters = []
                for value in values:
                    if value == "Under 1000":
                        range_filters.append({"range": {"Price": {"lt": 1000}}})
                    elif value == "1000 - 5000":
                        range_filters.append({"range": {"Price": {"gte": 1000, "lt": 5000}}})
                    elif value == "Over 5000":
                        range_filters.append({"range": {"Price": {"gte": 5000}}})
                if range_filters:
                    filter_clauses.append({"bool": {"should": range_filters, "minimum_should_match": 1}})
            else:
                # Term filters for other fields
                filter_clauses.append({"terms": {field: values}})
        if filter_clauses:
            if "bool" not in query["query"]["function_score"]["query"]:
                query["query"]["function_score"]["query"]["bool"] = {}
            query["query"]["function_score"]["query"]["bool"]["filter"] = filter_clauses

    res = es.search(index="clothing", body=query)
    results = res["hits"]["hits"]
    facets = res["aggregations"]

    return results, facets

# Added aggregations for certain features.


def main():
    st.title("Helpful Engineering Organization")

    # Session state to store selected filters
    if 'selected_filters' not in st.session_state:
        st.session_state.selected_filters = {}

    # Input: User enters search query
    search_query = st.text_input("Enter your search query")

    # Button: User triggers the search
    # Perform search when query changes or filters are applied
    if st.button("Search"):
        if search_query:
            # Perform the search and get results
            results, facets = search(search_query, st.session_state.selected_filters)

            # Display facets
            st.sidebar.header("Filter Results")

            def update_filters():
                st.session_state.selected_filters = {}
                for field in ["ProductBrand", "PrimaryColor", "Gender", "Price"]:
                    selected_values = st.sidebar.multiselect(
                        field,
                        options=facet_options[field],
                        default=st.session_state.selected_filters.get(field, [])
                    )
                    if selected_values:
                        st.session_state.selected_filters[field] = selected_values

            # Prepare facet options
            facet_options = {}
            for facet_field in ["ProductBrand", "PrimaryColor", "Gender"]:
                buckets = facets[facet_field]["buckets"]
                options = [bucket["key"] for bucket in buckets]
                facet_options[facet_field] = options

            # Price range options
            price_buckets = facets["PriceRange"]["buckets"]
            price_options = [bucket["key"] for bucket in price_buckets]
            facet_options["Price"] = price_options

            for field in ["ProductBrand", "PrimaryColor", "Gender", "Price"]:
                st.sidebar.multiselect(
                    field,
                    options=facet_options[field],
                    default=st.session_state.selected_filters.get(field, []),
                    key=field,
                    on_change=update_filters()
                )

            # Display search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if '_source' in result:
                        st.header(f"{result['_source']['ProductName']}")
                        st.write(f"Brand: {result['_source']['ProductBrand']}")
                        st.write(f"Price: {result['_source']['Price']}")
                        st.write(f"Color: {result['_source']['PrimaryColor']}")
                        st.write(f"Gender: {result['_source']['Gender']}")
                        st.write(f"Description: {result['_source']['Description']}")
                        st.divider()
        else:
            st.info("Enter a search query to begin.")

                    
if __name__ == "__main__":
    main()
