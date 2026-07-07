# Bidirectional Normalization

June 14, 2026

The propagation algorithm consistently converges to a fixed point for both uniform and random initialization.

I've noted that the ranking results revealed a hidden problem. Even after source degree normalization, some sources are still capable of consuming all credibility due to the graph structure.

To address this we introduce normalization on both sides of the bipartite graph.

## Previous propagation

The original propagation step allows for distribution of source credibility across the claims asserted by each source:

$$
q_j = \sum_i \frac{s_i}{d_i}
$$

where:

* $(s_i)$ = source credibility

* $(d_i)$ = number of claims made by source $(i)$

The claims then vote back onto sources:

$$
s_i' = \frac{1}{|C_i|}\sum_j q_j
$$

After each iteration we normalize:

$$
\sum_i s_i = 1
$$

## Bidirectional normalization

In v4 we additionally normalize claim support by the number of supporting sources:

$$
q_j = \frac{1}{|S_j|}\sum_i \frac{s_i}{d_i}
$$

where:

* $(|S_j|)$ = number of sources supporting claim $(j)$

The idea is simple: if many sources contribute to the same claim, we average that support instead of allowing it to accumulate indefinitely.

## Results

The updated propagation algorithm still converges to a stable fixed point whether the initialization was uniform or random.

Normalizing the claim support based on the number of supporting sources results in more balanced source credibility scores than normalizing source scores only.

## Current observations

The propagation scheme appears more stable now.

Most claims are still asserted by only a single source:

$$
\text{Average sources per claim} \approx 1.09
$$

This means the graph still contains little agreement information for credibility propagation.

Improving product matching and claim canonicalization may have a more noticeable impact than further changes to the propagation algorithm itself. Increasing overlap between sources may therefore be an important next step. Although, additional experiments are needed to separate the effects of graph structure from the propagation operator itself.
