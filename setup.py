# the setup to create the Weaviate object

import weaviate
import weaviate.classes as wvc

client = weaviate.connect_to_local(
    port=8080
)

if (client.collections.exists("Article")):
    client.collections.delete("Article")
    print("Deleted Article")
if (client.collections.exists("Paragraph")):
    client.collections.delete("Paragraph")
    print("Deleted Paragraph")



# create a class named Article
# Article has attributes: title
# Paragraph has attributes: text, order_id, and a vector embedding

article = client.collections.create(
    name="Article",
    properties=[
        wvc.Property(name="title", data_type=wvc.DataType.TEXT)
    ]
)

# create a class named Paragraph
# Paragraph has attributes: text, order_id, and a vector embedding

paragraph = client.collections.create(
    name="Paragraph",
    properties=[
        wvc.Property(name="order", data_type=wvc.DataType.INT),
        wvc.Property(name="text", data_type=wvc.DataType.TEXT),
        wvc.Property(name="article_uuid", data_type=wvc.DataType.TEXT),
    ],
)