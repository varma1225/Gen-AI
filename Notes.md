

# Generative AI  Notes

## Generative AI (Gen AI)

Generative AI is an AI system that can **generate new content** such as text, images, audio, video, or code based on patterns learned from existing data.

Example:

* ChatGPT → text
* DALL·E → images
* Copilot → code

---

## Intelligence

Intelligence is the ability to:

* Learn
* Understand
* Think
* Solve problems
* Adapt to new situations

---

## Artificial Intelligence (AI)

Artificial Intelligence is the ability of machines to perform tasks that normally require human intelligence such as:

* Learning
* Reasoning
* Problem-solving
* Decision-making

---

## Machine Learning (ML)

Machine Learning is a subset of AI where machines **learn from data instead of being explicitly programmed**.

### Types of Machine Learning

1. **Supervised Learning**
   Uses labeled data
   → Classification, Regression

2. **Unsupervised Learning**
   Uses unlabeled data
   → Clustering, Dimensionality Reduction

3. **Reinforcement Learning**
   Learns using rewards and penalties

---

## Deep Learning (DL)

Deep Learning is a subset of Machine Learning that uses **multi-layer neural networks** to learn complex patterns from large amounts of data.

### Used in:

* Image recognition
* Speech recognition
* Natural Language Processing

---

## Neural Networks

A Neural Network is a machine learning model inspired by the human brain that learns patterns using interconnected artificial neurons.

### Structure

1. Input Layer – Receives data
2. Hidden Layer(s) – Learns patterns
3. Output Layer – Produces result

---

## Tokens

A token is the smallest unit of text processed by an AI model.

Example:

Sentence:
`I am Varma`

Tokens:
`[I, am, Varma]`

(Real tokenization may differ slightly based on tokenizer.)

---

## Transformers

Transformers are neural network models that process all tokens in a sentence **in parallel** using a mechanism called **self-attention**.

They do NOT read word by word sequentially like RNNs.

---

## Parallelism

Parallelism means performing multiple computations at the same time instead of one after another.

Transformers use parallelism to achieve high speed.

---

# Day 3 – Embeddings

## Embeddings

Embeddings are dense numerical vectors that represent text, images, audio, or video in a form that machines can understand.

They capture **semantic meaning**.

 Similar content → closer vectors 
 Different content → far vectors

### Simple meaning:

> Embeddings are GPS coordinates of data in AI space.

---

## Dimensions

When text is converted into embeddings, it becomes a vector of numbers.

Each number = one dimension.

Example:

```
[0.12, -0.44, 0.89, 0.01, ...]
```

Each value is one dimension.

### Typical dimensions

| Data Type | Dimensions |
| --------- | ---------- |
| Text      | 384 – 3072 |
| Voice     | 192 – 512  |
| Image     | 512 – 1024 |

Examples:

* 128-dim → 128 numbers
* 384-dim → 384 numbers
* 768-dim → 768 numbers
* 1536-dim → 1536 numbers

---

## Vector

A vector is a numerical representation of data **along with its meaning**.

---

## Vector Database

A Vector Database is a database designed to store, manage, and search vectors (embeddings).

It supports **semantic similarity search**.

Examples:

* FAISS
* Chroma
* Pinecone
* Weaviate

---

## Why we use Vector Databases for Embeddings

We use vector databases because:

* Embeddings are high-dimensional vectors
* Normal databases cannot efficiently search similarity
* Vector DB uses ANN (Approximate Nearest Neighbor) algorithms
* Enables fast semantic search
* Essential for RAG systems

---
## RAG (Retrival Augmented Generation)

RAG is a technique where AI retrieves relevant data from your own documents and then generates accurate answers using that data.

User Question → Convert to Embedding → Search Vector Database → Retrieve Relevant Chunks → Send Chunks to LLM → Final Answer




