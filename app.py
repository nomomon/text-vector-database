import os

import streamlit as st
import re
import textract
import weaviate
import weaviate.classes as wvc

from sentence_transformers import SentenceTransformer

from transformers import BertForQuestionAnswering
from transformers import BertTokenizer



# the setup to create the Weaviate object
client = weaviate.connect_to_local(
    port=8080
)
articles = client.collections.get("Article")
paragraphs = client.collections.get("Paragraph")

# load bert (Question/Answer) model
bert_model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
bert_tokenizer = BertTokenizer.from_pretrained(bert_model_name)
bert_model = BertForQuestionAnswering.from_pretrained(bert_model_name)

# load sentence transformer model
transformer_model_name = 'sentence-transformers/multi-qa-mpnet-base-dot-v1'
sentence_transformer = SentenceTransformer(transformer_model_name)


# -----
#  UI
# -----


st.title("Information Retrieval with Weaviate")

retrieval_tab, upload_tab, documents_tab = st.tabs(["Retrieval", "Upload", "Documents"])

with retrieval_tab:
    st.header("Retrieval")
    st.write("This is the retrieval tab")
    query = st.text_area("Enter your query here")

    if st.button("Search"):
        # search in weaviate
        st.write("Searching in Weaviate")

        # get embeddings
        query_embedding = sentence_transformer.encode([query])

        # search
        results = paragraphs.query.near_vector(
            near_vector=query_embedding[0],
            limit=10,
            return_metadata=wvc.query.MetadataQuery(distance=True), 
        )

        # show results
        st.write("Done searching in Weaviate")
        st.write("Results:")
        with st.expander("Show slices of text"):
            for r in results.objects:
                article_uuid = r.properties["article_uuid"]
                article = articles.query.fetch_object_by_id(article_uuid)

                text = r.properties["text"]
                
                # highlight the section that answers the question
                inputs = bert_tokenizer.encode_plus(query, text, return_tensors="pt", add_special_tokens=True)
                sp, ep = bert_model(**inputs).values()

                tokens = bert_tokenizer.convert_ids_to_tokens(inputs["input_ids"].squeeze().tolist())
                ans = bert_tokenizer.convert_tokens_to_string(tokens[sp.argmax(): ep.argmax() + 1])
                
                text = text.replace(ans, f"**{ans}**")

                st.markdown(f"Source: `{article.properties['title']}`")
                st.markdown(f"Answer: {text}")
                st.markdown(f"Distance: `{r.metadata.distance}`")
                st.write("---")
        


with upload_tab:
    st.header("Upload")
    st.write("This is the upload tab")
    uploaded_file = st.file_uploader("Choose a file", type="pdf")

    if uploaded_file is not None:
        # steamlit loader
        st.write("File uploaded, processing...")
        
        # save file to disk (tmp)
        with open("tmp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # extract text from pdf
        text = textract.process("tmp.pdf").decode("utf-8")
        lines = text.split("\n")
        lines = [line for line in lines if line != ""]
        lines = [line for line in lines if not re.match(r"^\d+$", line)]
        lines = [line for line in lines if len(line) > 10]
        text = " ".join(lines)
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"www\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.split(".")

        # delete file from disk
        os.remove("tmp.pdf")

        # split text into slices of 5 sentences
        slices_of_text = []
        with st.expander("Show slices of text"):
            for i in range(0, len(text), 5):
                t = " ".join(text[i:i+5])
                if len(t) > 2 * 1e3: continue
                slices_of_text.append(t)
                
                st.write(t)
                st.write("---")


        st.write("Uploading to Weaviate...")
        
        # create the document
        article_uuid = articles.data.insert(
            properties={
                "title": uploaded_file.name,
            },
        )

        # get embeddings
        embeddings = sentence_transformer.encode(slices_of_text)

        # upload embeddings and text to weaviate
        progress_bar = st.progress(0)
        for i, t in enumerate(slices_of_text):
            paragraphs.data.insert(
                properties={
                    "text": t,
                    "order": i,
                    "article_uuid": article_uuid,
                },
                vector=embeddings[i]
            )
            progress_bar.progress(i / len(slices_of_text))
        progress_bar.progress(100)
        
        st.write("Done")



with documents_tab:
    # place to show all documents in the database
    # and to delete them if necessary

    st.header("Documents")
    st.write("This is the documents tab. Here you can delete documents.")
    
    def delete_document(uuid):
        def func():
            paragraphs.data.delete_many(
                where=wvc.query.Filter("article_uuid").equal(uuid)
            )
            articles.data.delete_by_id(uuid)
        return func

    # show all documents
    if articles.aggregate.over_all(total_count=True).total_count == 0:
        st.write("No documents found")
    else:
        for article in articles.iterator():
            col1, col2 = st.columns(2)
            col1.button("Delete", key=article.uuid, on_click=delete_document(article.uuid))
            col2.markdown(f"`{article.properties['title']}`")
            st.write("---")