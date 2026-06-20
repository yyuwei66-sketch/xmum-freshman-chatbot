生成一个演示文稿，讲解当前项目的retrieval.py部分，全部内容用英文书写，请注意我下面的内容不要全部放进去，保留概括性的关键，以视觉效果为优先，如有需要可以参考src/retreval.py里的代码实现

第一页是标题"Retrieval-based chatbot"，右下角附上演讲人；“Zhang Jinyu AIT2509057"，形式与本目录下其他的html文件署名方式统一

第二页介绍 retrieval.py 中的检索分数计算（我希望放进一页，但若内容过密集就拆成合适的页数，以总分结构呈现，结构要清晰）：

1. Three retrieval scores

说明系统不是只依赖单一相似度，而是同时计算三类检索分数：

- Sentence embedding similarity: the user question is encoded with the SentenceTransformer model, then compared with pre-computed FAQ question embeddings. Since embeddings are normalized, the dot product works like cosine similarity. This score captures semantic similarity between the whole user question and each FAQ question.
- TF-IDF sentence similarity: the user question is transformed by a TF-IDF vectorizer and compared with all FAQ questions using cosine similarity. This score captures lexical overlap, especially exact words and short phrases.
- Token-level embedding similarity: the user question is tokenized, stop words are removed, and each query token is compared semantically with tokens from each FAQ candidate's question and keywords. For each query token, the system keeps its best semantic match in the candidate and averages these best matches. This score helps emphasize important local terms such as “certificate”, “dormitory”, or “eWallet”.

请在演示稿中写出三类检索分数的计算公式：

- Sentence embedding similarity:
  - Let the user question embedding be q and the FAQ question embedding be d_i.
  - Because embeddings are unit-normalized, the similarity is:
  - s_embed(i) = q · d_i = cos(q, d_i)
- TF-IDF sentence similarity:
  - Let the TF-IDF vector of the user question be v_q and the TF-IDF vector of FAQ question i be v_i.
  - The score is cosine similarity:
  - s_tfidf(i) = (v_q · v_i) / (||v_q|| ||v_i||)
- Token-level embedding similarity:
  - Let the query tokens be T_q = {t_1, t_2, ..., t_m}.
  - Let the candidate tokens for FAQ i be T_i = {c_1, c_2, ..., c_n}, built from the FAQ question and keywords.
  - For each query token, find the most similar candidate token, then average:
  - s_token(i) = (1 / m) Σ_{a=1}^{m} max_{b=1}^{n} cos(e(t_a), e(c_b))

第二页写融合方式：2. Three-way score fusion

解释 retrieval.py 使用 Reciprocal Rank Fusion (RRF) 融合三路检索结果，而不是简单地把原始分数相加。具体来说：

- Each retrieval score produces its own ranking of FAQ candidates.
- The rankings from sentence embeddings, TF-IDF, and token-level embeddings are converted into reciprocal-rank scores.
- These reciprocal-rank scores are normalized into a final RRF score.
- The benefit is that the system becomes more robust: a candidate that ranks consistently high across different retrieval methods is preferred, even if the raw score scales are different.

请写出 RRF 的计算公式：

- Let r_embed(i), r_tfidf(i), and r_token(i) be the one-based ranks of FAQ candidate i from the three retrieval methods.
- retrieval.py uses K = 60.
- Raw RRF score:
  - RRF_raw(i) = 1 / (K + r_embed(i)) + 1 / (K + r_tfidf(i)) + 1 / (K + r_token(i))
- Normalized RRF score:
  - RRF(i) = RRF_raw(i) / (3 / (K + 1))
- This normalized score is clipped to the range [0, 1].

可在演示稿中用一个简短例子解释：如果某个 FAQ 在 semantic ranking、lexical ranking、token ranking 中都比较靠前，它会获得较高的 final score。

第三页：3. Keyword tie-breaker

说明 Keyword tie-breaker 不是主要排序依据，而是在 RRF 分数非常接近时使用的辅助机制：

- The system selects the most important non-stopword query token using IDF from the FAQ corpus.
- This important keyword is embedded and compared with each candidate's token embeddings.
- When two candidates have very close RRF scores, the candidate whose tokens are semantically closer to the important keyword is ranked higher.

请写出 Keyword tie-breaker 的计算方式：

- First, choose the important keyword k from the user query:
  - k = argmax_{t in query tokens} IDF(t)
- Then compare this keyword with every token in candidate FAQ i:
  - s_keyword(i) = max_{c in T_i} cos(e(k), e(c))
- The final sort key mainly uses the RRF score. Keyword similarity is only used when candidates fall into the same close-score bucket:
  - bucket(i) = round(RRF(i) / ε)
  - retrieval.py uses ε = 0.01
- Candidates are sorted approximately by:
  - bucket(i), then s_keyword(i), then RRF(i)

强调这个设计的作用：当多个 FAQ 的整体相似度接近时，系统会更关注用户问题中最有区分度的关键词，从而减少相近问题之间的误选。

第四页补充 fallback logic：如果检索证据不足，例如没有 lexical anchor、final RRF score 太低，或 evidence score 太低，系统不会强行返回 FAQ，而是回复 “Sorry, I do not have an answer for that.”

最后一页展示测试结果，绘制表格展现retrieval-based chatbot的测试效果

请在最后一页加入以下 retrieval evaluation 表格，标题可写为 “Retrieval Evaluation on Extended Query Set”。说明测试集来自 `data/train&test/extend_data.jsonl`，每个 FAQ id 有四种 query variant：standard, colloquial, incomplete, and paraphrase。评价方式是：每个 query 应该检索回相同 id 的 FAQ；Top-1 表示第一命中是否正确，Top-4 表示第一命中或 related questions 中是否包含正确 FAQ。

| Query type | N | Top-1 Accuracy | Top-4 Recall | Fallback Rate | Average Score |
|---|---:|---:|---:|---:|---:|
| Overall | 2460 | 0.741 | 0.910 | 0.010 | 0.984 |
| Standard | 615 | 0.964 | 0.989 | 0.005 | 0.998 |
| Colloquial | 615 | 0.567 | 0.826 | 0.021 | 0.972 |
| Incomplete | 615 | 0.725 | 0.938 | 0.007 | 0.981 |
| Paraphrase | 615 | 0.709 | 0.886 | 0.007 | 0.985 |

表格下方请给出一句英文解读：The system performs very well on standard questions, but colloquial queries are much harder. Since Top-4 is much higher than Top-1, many correct answers are already retrieved but not ranked first, suggesting that ranking refinement is the main improvement direction.

同时在最后一页或附加 case study 区域给出一个误判样例，重点展示 “English classes”：

- Query: `English classes`
- Expected FAQ id: `AA_015`
- Expected question: `What should I do if I can't understand the English-only instruction at the beginning? Any adaptation tips?`
- Retrieved FAQ id: `AA_017`
- Retrieved question: `What are the English language requirements for international students applying to foundation programmes?`
- Score: `0.968`
- Error explanation: The short query only contains a broad lexical anchor, “English”. The retriever therefore confuses “English-medium class adaptation” with “English language requirement”, because both candidates share semantically similar terms but refer to different student needs.
