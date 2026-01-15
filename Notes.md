**Generative AI**

 **Gen AI**
 
 Generative AI is an AI system that generates new content like text, images, or code based on patterns learned from existing data

 **Intelligence** :Intelligence is the ability to learn, understand, think, solve problems, and adapt to new situations.

 **Artifical Intelligence**:Artificial Intelligence is the ability of machines to perform tasks that normally require human intelligence such as learning, reasoning, problem-solving, and decision-making.


**Machine Learning (ML)**

Machine Learning is a subset of AI where machines learn patterns from data instead of being explicitly programmed.

Types of ML

1.Supervised Learning – Labeled data (Classification, Regression)

2.Unsupervised Learning – Unlabeled data (Clustering, Dimensionality Reduction)

3.Reinforcement Learning – Learning through rewards and penalties

**Deep Learning (DL)**

Deep Learning is a subset of Machine Learning that uses multi-layer neural networks to learn complex patterns from large data.

Used in:Image recognition,Speech recognition,Natural language processing

**NEURAL NETWORKS**

A Neural Network is a machine learning model inspired by the human brain that learns patterns from data using interconnected layers of artificial neurons.
🔹 Structure of a Neural Network

      1.Input Layer – Receives data

      2.Hidden Layer(s) – Learns patterns

      3.Output Layer – Gives final result
      

**Tokens**

A token is the smallest unit of text that an AI model processes

Ex: i am varma  here tokens are [i , am , varma]

**Transformers**

Transformers can process an entire sentence in one go instead of reading words one by one, because they use self-attention to look at all tokens simultaneously.

**Parallelsim**

Parallelism means performing multiple computations at the same time instead of one after another.

**Day_3**(09/1/26)


**Embeddings**

embeddings are dense numeric vectors that represent text (words, sentences, documents) or other data (images, audio) in a format that computers can reason about. Think of them as points in a high-dimensional space where similar content is closer together.

Embeddings  are the GPS coordinates of a word.

**Dimensions**

When text is converted into an embedding, it becomes a vector of numbers.

Each number = one dimension.

[0.12, -0.44, 0.89, 0.01, ...]  ← each value is one dimension

Text → 384 to 3072
Voice → 192 to 512
Image → 512 to 1024




So,

128-dim embedding → 128 numbers

384-dim embedding → 384 numbers

768-dim embedding → 768 numbers

1536-dim embedding → 1536 numbers



**Vector**:numerical representation of data + its meaning 

**Vector DataBase**

A vector database is a database designed to store, manage, and search vectors (embeddings) instead of normal text or numbers.

1.why we use only vector data base to store embeddings 

We use vector databases to store embeddings because they are optimized for high-dimensional vectors and allow fast semantic similarity search, which normal databases cannot efficiently support.
 
        
