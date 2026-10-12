# RAG Evaluation: dense vs hybrid retrieval

Notebook: **eval test**

## Summary

| Method | Avg retrieval (ms) | Avg LLM (ms) | Retrieval hit | Avg hit rank | Relevance | Groundedness | Completeness |
|---|---|---|---|---|---|---|---|
| dense | 11.46 | 6082.97 | 5/5 | 1.00 | 5.00 | 4.67 | 4.83 |
| hybrid | 13.84 | 6774.60 | 5/5 | 1.00 | 5.00 | 5.00 | 4.83 |

Retrieval hit = a retrieved chunk contained an expected keyword (out-of-scope questions excluded). Scores are 1-5 from an LLM judge. Retrieval time is the median of 3 runs after warm-up.

## Q1 (factual): What is retrieval-augmented generation?

### dense
- Retrieval: 9.2 ms | LLM: 1274 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 4. Provides a solid definition supported by excerpts, though omits some ancillary details like its 2020 origin.

**Retrieved chunks:**
- `e1957d80-15` (Retrieval-augmented generation - Wikipedia, score 0.610): Jiang, Jie; Cui, Bin (March 2026). "Retrieval-Augmented Generation for AI-Generated Content: A Survey". Data Science and Engineering. 11 (1): 1–29. doi:10.1007/...
- `e1957d80-0` (Retrieval-augmented generation - Wikipedia, score 0.591): Retrieval-augmented generation Retrieval-augmented generation (RAG) is a technique that enables large language models (LLMs) to retrieve and incorporate new inf...
- `e1957d80-4` (Retrieval-augmented generation - Wikipedia, score 0.547): did not "know" or "understand" the context of the title, generating a false statement.[3] LLMs with RAG are programmed to prioritize new information. This techn...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.538): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...
- `e1957d80-14` (Retrieval-augmented generation - Wikipedia, score 0.525): is that the model may combine details from multiple sources producing responses that merge outdated and updated information in a misleading manner. According to...

**Answer:**

Retrieval‑augmented generation (RAG) is a technique that couples a large language model with an external, non‑parametric memory: at inference time the model first retrieves relevant documents from a specified data source and then incorporates that retrieved information into its response. This lets the LLM supplement its pre‑training knowledge with domain‑specific or up‑to‑date content that isn’t in its original training set [2][4].

### hybrid
- Retrieval: 13.3 ms | LLM: 1375 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Accurately defines RAG using the provided excerpts.

**Retrieved chunks:**
- `e1957d80-14` (Retrieval-augmented generation - Wikipedia, score 0.032): is that the model may combine details from multiple sources producing responses that merge outdated and updated information in a misleading manner. According to...
- `e1957d80-0` (Retrieval-augmented generation - Wikipedia, score 0.032): Retrieval-augmented generation Retrieval-augmented generation (RAG) is a technique that enables large language models (LLMs) to retrieve and incorporate new inf...
- `e1957d80-15` (Retrieval-augmented generation - Wikipedia, score 0.031): Jiang, Jie; Cui, Bin (March 2026). "Retrieval-Augmented Generation for AI-Generated Content: A Survey". Data Science and Engineering. 11 (1): 1–29. doi:10.1007/...
- `e1957d80-4` (Retrieval-augmented generation - Wikipedia, score 0.031): did not "know" or "understand" the context of the title, generating a false statement.[3] LLMs with RAG are programmed to prioritize new information. This techn...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.030): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...

**Answer:**

Retrieval‑augmented generation (RAG) is a method that lets large language models pull in information from external data sources and combine it with the model’s own knowledge when answering a query. By first retrieving a set of documents and then using those documents as context, the LLM can supplement its pre‑trained training data with domain‑specific, up‑to‑date, or otherwise unavailable information【2†L1-L4】. This approach enhances the model’s ability to provide accurate, current responses that go beyond what was learned during initial training【4†L1-L3】.

## Q2 (keyword): Which datasets does the milestone slide mention for loading motion data?

### dense
- Retrieval: 10.7 ms | LLM: 596 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Correctly lists both datasets mentioned in the slide.

**Retrieved chunks:**
- `004bebee-4` (FloodDiffusion_Milestone -1.pptx, Slide 5, score 0.557): FloodDiffusion  •  Milestone 1 4. Repository & Folder Structure Where the important pieces live configs/ Training and generation configuration datasets/ HumanML...
- `004bebee-7` (FloodDiffusion_Milestone -1.pptx, Slide 8, score 0.461): FloodDiffusion  •  Milestone 1 7. Inputs, Outputs & Demo Cases What we will test Input text: prompt string/listlength: desired frame counttext_end: optional t...
- `004bebee-10` (FloodDiffusion_Milestone -1.pptx, Slide 11, score 0.452): FloodDiffusion  •  Milestone 1 10. Takeaways & What We Will Demonstrate Milestone 1 → Milestone 2 ✓ Connected the diffusion-forcing idea to the actual VAE + DiT...
- `004bebee-8` (FloodDiffusion_Milestone -1.pptx, Slide 9, score 0.450): FloodDiffusion  •  Milestone 1 8. Challenges We Identified Practical issues before implementation Environment Repository setup includes requirements and  Flash ...
- `004bebee-1` (FloodDiffusion_Milestone -1.pptx, Slide 2, score 0.448): FloodDiffusion  •  Milestone 1 1. What We Needed to Understand Milestone 1 focus Paper idea Why diffusion forcing needs to be tailored for  streaming motion gen...

**Answer:**

The slide lists the **HumanML3D** and **BABEL** datasets as the loaders for motion data【1】.

### hybrid
- Retrieval: 11.5 ms | LLM: 618 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Correctly lists HumanML3D and BABEL as the datasets mentioned.

**Retrieved chunks:**
- `004bebee-4` (FloodDiffusion_Milestone -1.pptx, Slide 5, score 0.033): FloodDiffusion  •  Milestone 1 4. Repository & Folder Structure Where the important pieces live configs/ Training and generation configuration datasets/ HumanML...
- `004bebee-10` (FloodDiffusion_Milestone -1.pptx, Slide 11, score 0.032): FloodDiffusion  •  Milestone 1 10. Takeaways & What We Will Demonstrate Milestone 1 → Milestone 2 ✓ Connected the diffusion-forcing idea to the actual VAE + DiT...
- `004bebee-1` (FloodDiffusion_Milestone -1.pptx, Slide 2, score 0.030): FloodDiffusion  •  Milestone 1 1. What We Needed to Understand Milestone 1 focus Paper idea Why diffusion forcing needs to be tailored for  streaming motion gen...
- `e1957d80-5` (Retrieval-augmented generation - Wikipedia, score 0.028): by incorporating an information-retrieval mechanism that allows models to access and utilize additional data beyond their original training set. Ars Technica no...
- `004bebee-0` (FloodDiffusion_Milestone -1.pptx, Slide 1, score 0.028): FloodDiffusion  •  Milestone 1 FloodDiffusion Milestone 1 — Code Review & Implementation Tailored Diffusion Forcing for Streaming Motion Generation Paper → Arch...

**Answer:**

The milestone slide lists the **HumanML3D** and **BABEL** datasets as the loaders used for motion data【1】.

## Q3 (conceptual): How does RAG reduce hallucinations?

### dense
- Retrieval: 11.1 ms | LLM: 8243 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Answer directly explains the grounding mechanism supported by the excerpts

**Retrieved chunks:**
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.370): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-13` (Retrieval-augmented generation - Wikipedia, score 0.305): it does not remove it entirely. Additionally, LLMs may struggle to recognize when they lack sufficient information to provide a reliable response. Without speci...
- `e1957d80-1` (Retrieval-augmented generation - Wikipedia, score 0.250): based on authoritative sources. The technique was first proposed in 2020 and has since become a widely adopted approach in modern AI systems. RAG improves LLMs ...
- `e1957d80-4` (Retrieval-augmented generation - Wikipedia, score 0.230): did not "know" or "understand" the context of the title, generating a false statement.[3] LLMs with RAG are programmed to prioritize new information. This techn...
- `e1957d80-7` (Retrieval-augmented generation - Wikipedia, score 0.230): Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning. Applications [edit] ...

**Answer:**

Retrieval‑augmented generation (RAG) cuts down on hallucinations by grounding the model’s output in external, up‑to‑date text rather than relying solely on its static training knowledge. When a prompt is processed, RAG first fetches relevant passages from databases, uploaded documents or web sources and feeds that retrieved material into the language model. Because the model can directly quote or reference these authoritative excerpts, it is more likely to “stick to the facts” and less likely to fabricate information — a key way the technique mitigates AI hallucinations【3†L1-L4】.

### hybrid
- Retrieval: 14.6 ms | LLM: 14486 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Answer is fully supported and covers key points from excerpts.

**Retrieved chunks:**
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.033): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-1` (Retrieval-augmented generation - Wikipedia, score 0.032): based on authoritative sources. The technique was first proposed in 2020 and has since become a widely adopted approach in modern AI systems. RAG improves LLMs ...
- `e1957d80-13` (Retrieval-augmented generation - Wikipedia, score 0.031): it does not remove it entirely. Additionally, LLMs may struggle to recognize when they lack sufficient information to provide a reliable response. Without speci...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.030): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...
- `e1957d80-4` (Retrieval-augmented generation - Wikipedia, score 0.030): did not "know" or "understand" the context of the title, generating a false statement.[3] LLMs with RAG are programmed to prioritize new information. This techn...

**Answer:**

Retrieval‑augmented generation lowers the chance that a model will “hallucinate” by pulling in concrete, external text at inference time and forcing the model to generate from that evidence rather than relying solely on its internal memorized parameters.  By blending the LLM’s generation with a web‑search or document‑lookup step, RAG lets the model “stick to the facts” found in the retrieved sources, and those sources can be shown to the user for verification【2†L1-L4】【2†L5-L7】.  This grounding in real‑world documents reduces—though does not eliminate—the frequency of fabricated or inaccurate statements.

## Q4 (multi-part): What are the benefits and limitations of RAG?

### dense
- Retrieval: 11.2 ms | LLM: 12245 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 3, completeness 5. Answer is on topic and thorough, but includes a couple claims (e.g., medical example, Bard case) not directly supported by the excerpts.

**Retrieved chunks:**
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.465): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-13` (Retrieval-augmented generation - Wikipedia, score 0.383): it does not remove it entirely. Additionally, LLMs may struggle to recognize when they lack sufficient information to provide a reliable response. Without speci...
- `e1957d80-1` (Retrieval-augmented generation - Wikipedia, score 0.372): based on authoritative sources. The technique was first proposed in 2020 and has since become a widely adopted approach in modern AI systems. RAG improves LLMs ...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.361): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...
- `e1957d80-7` (Retrieval-augmented generation - Wikipedia, score 0.348): Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning. Applications [edit] ...

**Answer:**

**Benefits of Retrieval‑augmented Generation (RAG)**  

- **Higher factual accuracy and fewer hallucinations** – By pulling up‑to‑date text from external sources, RAG helps LLMs “stick to the facts” and reduces AI hallucinations [3][4].  
- **Less frequent model retraining** – Because the model can retrieve new information at inference time, the need to retrain the LLM with fresh data is lowered, saving computational and financial costs [3][4].  
- **Transparency and verifiability** – Retrieved passages can be shown to users, letting them cross‑check the cited sources [3][4].  
- **Grounding in external or rapidly changing knowledge** – RAG is used where responses must be anchored in up‑to‑date material (e.g., medical knowledge) [5].  
- **Hybrid search improves retrieval** – Combining vector (semantic) search with traditional full‑text search can capture key facts that a pure vector search might miss [1].  
- **Efficiency gains** – The overall workflow can be more efficient than constantly re‑training large models [3][4].

**Limitations of RAG**  

- **Hallucinations are not eliminated** – The LLM can still hallucinate around the retrieved material, so RAG is not a complete solution to hallucination [1].  
- **Residual need for retraining** – RAG reduces but does not entirely remove the requirement to fine‑tune or retrain the model [1].  
- **Difficulty recognizing insufficient information** – Without specific training, models may generate answers even when they should express uncertainty, failing to detect when they lack enough knowledge [1][2].  
- **RAG‑related poisoning and misleading sources** – The system may retrieve factually correct yet context‑misleading documents, leading to incorrect conclusions or merging outdated and updated facts [2].  
- **Struggles with conflicting information** – When sources disagree, RAG models may have trouble deciding which is accurate [2].  
- **Persisting errors despite RAG** – Real‑world cases (e.g., Google’s Bard giving wrong data about the James Webb telescope) show that RAG does not guarantee error‑free outputs [4].  

Thus, RAG offers clearer, more up‑to‑date, and cost‑effective generation, but it still faces challenges with hallucinations, source reliability, and the model’s ability to know its own limits.

### hybrid
- Retrieval: 13.3 ms | LLM: 9777 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 4. Answer is relevant and well‑grounded but omits some benefits like efficiency and cost gains mentioned in the excerpts.

**Retrieved chunks:**
- `e1957d80-13` (Retrieval-augmented generation - Wikipedia, score 0.032): it does not remove it entirely. Additionally, LLMs may struggle to recognize when they lack sufficient information to provide a reliable response. Without speci...
- `e1957d80-7` (Retrieval-augmented generation - Wikipedia, score 0.032): Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning. Applications [edit] ...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.031): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...
- `e1957d80-5` (Retrieval-augmented generation - Wikipedia, score 0.030): by incorporating an information-retrieval mechanism that allows models to access and utilize additional data beyond their original training set. Ars Technica no...
- `e1957d80-1` (Retrieval-augmented generation - Wikipedia, score 0.030): based on authoritative sources. The technique was first proposed in 2020 and has since become a widely adopted approach in modern AI systems. RAG improves LLMs ...

**Answer:**

**Benefits of Retrieval‑Augmented Generation (RAG)**  

- **Better grounding and transparency** – By pulling external text and attaching citations, RAG lets users verify the source of each claim, increasing trustworthiness [3][5].  
- **Reduced hallucinations** – Access to up‑to‑date, authoritative documents helps keep the model’s output factual and lowers the chance of invented answers [5].  
- **Lower retraining costs** – New information can be added to the external knowledge base instead of re‑training the whole model, saving computational and financial resources [4][5].  
- **Ability to handle fresh or domain‑specific data** – RAG is useful in settings where responses must reflect constantly changing or specialized knowledge (e.g., healthcare, finance) [2].  
- **Flexibility in data types** – It can retrieve from unstructured text, semi‑structured records, or structured knowledge graphs [4].  
- **Potential for quality improvements** – Extra steps such as re‑ranking, context selection, or fine‑tuning can be added to the RAG pipeline to boost output accuracy [2].

**Limitations of RAG**  

- **Does not eliminate hallucinations** – While it reduces them, RAG cannot fully prevent the model from producing incorrect information [5][3].  
- **Vulnerability to misleading or conflicting sources** – Retrieved documents may be factually correct but taken out of context, or multiple sources may conflict, leading the model to merge outdated and updated details into a misleading answer [1].  
- **Model’s self‑awareness remains limited** – Even with retrieval, LLMs may fail to recognize when they lack sufficient knowledge and may still generate confident but unreliable responses [1].  
- **RAG cannot solve all LLM problems** – It helps mitigate some errors but does not address every limitation inherent to large language models [3].

## Q5 (keyword): What does the hybrid search section say about combining vector and keyword search?

### dense
- Retrieval: 10.1 ms | LLM: 11285 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Accurately reflects the hybrid search description and cites supporting excerpts.

**Retrieved chunks:**
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.598): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-8` (Retrieval-augmented generation - Wikipedia, score 0.567): of a word, are typically dictionary-length and contain mostly zeros. Dense vectors, which encode meaning, are more compact and contain fewer zeros. Various enha...
- `e1957d80-11` (Retrieval-augmented generation - Wikipedia, score 0.469): giving domain knowledge during training, Retro needs less focus on the domain and can devote its smaller weight resources only to language semantics. The redesi...
- `e1957d80-9` (Retrieval-augmented generation - Wikipedia, score 0.424): sparse dot products over dense vector operations.[9] - Other retrieval techniques focus on improving accuracy by refining how documents are selected. Some retri...
- `e1957d80-19` (Retrieval-augmented generation - Wikipedia, score 0.412): Linguistics. 11: 1316–1331. arXiv:2302.00083. doi:10.1162/tacl_a_00605. Retrieved 16 March 2025. - ↑ Borgeaud, Sebastian; Mensch, Arthur (2021). "Improving lang...

**Answer:**

The hybrid‑search section explains that a “hybrid” approach merges a conventional keyword (full‑text) search with a vector‑based semantic search. First, a traditional text search is run, then its hits are combined with the text chunks that are linked to the vectors retrieved by the semantic search. The merged set of passages is then rescored or reranked (e.g., with effective scoring) and supplied to the language model for generation [1].  

In addition, hybrid methods can fuse dense vector embeddings with sparse one‑hot (keyword) vectors, exploiting the efficiency of sparse dot‑product operations while retaining the semantic power of dense vectors [2][4].

### hybrid
- Retrieval: 12.8 ms | LLM: 8869 ms | hit: True (rank 1)
- Scores: relevance 5, groundedness 5, completeness 5. Answer accurately reflects the hybrid search description from the excerpts.

**Retrieved chunks:**
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.033): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-11` (Retrieval-augmented generation - Wikipedia, score 0.032): giving domain knowledge during training, Retro needs less focus on the domain and can devote its smaller weight resources only to language semantics. The redesi...
- `e1957d80-8` (Retrieval-augmented generation - Wikipedia, score 0.032): of a word, are typically dictionary-length and contain mostly zeros. Dense vectors, which encode meaning, are more compact and contain fewer zeros. Various enha...
- `e1957d80-9` (Retrieval-augmented generation - Wikipedia, score 0.031): sparse dot products over dense vector operations.[9] - Other retrieval techniques focus on improving accuracy by refining how documents are selected. Some retri...
- `e1957d80-2` (Retrieval-augmented generation - Wikipedia, score 0.030): and financial costs.[1] Beyond efficiency gains, RAG also allows LLMs to include sources in their responses, so users can verify the cited sources. This provide...

**Answer:**

The hybrid‑search section explains that because pure vector (semantic) searches can omit important facts, a common fix is to run a traditional full‑text/keyword search in parallel, merge those keyword results with the text chunks tied to the retrieved vectors, and then pass this combined “hybrid” text—often after applying scoring or reranking—into the language model for generation【1】.  It also notes that hybrid approaches can mix dense vector representations with sparse (keyword‑style) one‑hot vectors to leverage both types of similarity【3】.

## Q6 (out-of-scope): Who won the 2018 FIFA World Cup?

### dense
- Retrieval: 16.3 ms | LLM: 2855 ms | hit: None (rank None)
- Scores: relevance 5, groundedness 5, completeness 5. Correctly states no answer is in the sources

**Retrieved chunks:**
- `e1957d80-0` (Retrieval-augmented generation - Wikipedia, score 0.099): Retrieval-augmented generation Retrieval-augmented generation (RAG) is a technique that enables large language models (LLMs) to retrieve and incorporate new inf...
- `e1957d80-14` (Retrieval-augmented generation - Wikipedia, score 0.082): is that the model may combine details from multiple sources producing responses that merge outdated and updated information in a misleading manner. According to...
- `e1957d80-9` (Retrieval-augmented generation - Wikipedia, score 0.068): sparse dot products over dense vector operations.[9] - Other retrieval techniques focus on improving accuracy by refining how documents are selected. Some retri...
- `e1957d80-20` (Retrieval-augmented generation - Wikipedia, score 0.064): Pays $6 Million on GPT Training to Sway US Youth Opinion on Gaza". Inside Telecom. 2025-09-30. Retrieved 2026-01-11. - ↑ Cordall, Simon Speakman. "Spinning geno...
- `e1957d80-7` (Retrieval-augmented generation - Wikipedia, score 0.061): Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning. Applications [edit] ...

**Answer:**

I couldn't find the answer to that question in the provided sources.

### hybrid
- Retrieval: 17.6 ms | LLM: 5523 ms | hit: None (rank None)
- Scores: relevance 5, groundedness 5, completeness 5. Correctly identified that the excerpts lack the answer.

**Retrieved chunks:**
- `e1957d80-9` (Retrieval-augmented generation - Wikipedia, score 0.030): sparse dot products over dense vector operations.[9] - Other retrieval techniques focus on improving accuracy by refining how documents are selected. Some retri...
- `e1957d80-4` (Retrieval-augmented generation - Wikipedia, score 0.030): did not "know" or "understand" the context of the title, generating a false statement.[3] LLMs with RAG are programmed to prioritize new information. This techn...
- `e1957d80-14` (Retrieval-augmented generation - Wikipedia, score 0.030): is that the model may combine details from multiple sources producing responses that merge outdated and updated information in a misleading manner. According to...
- `e1957d80-12` (Retrieval-augmented generation - Wikipedia, score 0.029): in it. Hybrid search [edit] Sometimes vector database searches (aka semantic search technique) can miss key facts needed to answer a user's question. One way to...
- `e1957d80-7` (Retrieval-augmented generation - Wikipedia, score 0.029): Some models incorporate extra steps to improve output, such as the re-ranking of retrieved information, context selection, and fine-tuning. Applications [edit] ...

**Answer:**

I couldn't find the answer to that question in the provided sources.
