# Information Retrieval: Vector Database

This repository contains the code for a simple implementation of a vector database. It can absorb pdf files, which are split into groups of sentences and then vectorized. The vectors are stored in a [Weaviate](https://weaviate.io/) database, which can be queried for similar sentences.

The database then can be queried for similar sentences to a given sentence or a question. The similarity is calculated by the cosine similarity of the vectors. The results are then displayed in a simple web interface. In addition, the potential answer is highlighted in the original text.

Models used are:
- `sentence-transformers/multi-qa-mpnet-base-dot-v1`
    - This model is used to calculate the vectors of the sentences and questions.
- `bert-large-uncased-whole-word-masking-finetuned-squad`
    - This model is used to find and highlight the answer to a question in a given text.


## Installation

Set up a virtual environment with
```
python3 -m venv .venv
```

Activate the virtual environment with
```
source .venv/bin/activate
```

Install Python requirements with
```
pip3 install -r requirements.txt
```

Start the Weaviate server at `localhost:8080` with
```
docker-compose up -d --build
```

Run the setup of the Weaviate database with
```
python3 setup.py
```

## Usage

Start the virtual environment with (if not already active)
```
source .venv/bin/activate
```

Start the Streamlit app with
```
streamlit run app.py
```

Start the Docker container with (if not already running)
```
docker-compose up -d --build
```

## Turn off

Stop the Docker container with
```
docker-compose down
```

Deactivate the virtual environment with
```
deactivate
```

## Tunneled access

If you want to access the app from outside your local network, you can use [ngrok](https://ngrok.com/). Follow the installation instructions on their [website](https://ngrok.com/docs/getting-started/). 

After that, make sure Streamlit is running and you can start the tunnel with
```
ngrok http http://localhost:8501
```