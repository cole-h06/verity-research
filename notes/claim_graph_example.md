# Claim Graph Example

Let's say several sources publish specifications of a laptop's display.

One set of sources claim that:

- screen_brightness_nits = 300 nits

While another one claims that:

- screen_brightness_nits = 250 nits

These values can be represented as graph claims.

Each source forms an edge to the claim it asserts:

source_id -> claim_id

This would create a structure like this, where:

- source nodes are connected to claims,
- claims accumulate support from many source nodes,
- conflicting claims compete for reinforcement

![Assertions Graph](../images/assertions.png)

![Claims Graph](../images/claims.png)

In the above images,

- claim 892 = screen_brightness_nits : 300 nits
- claim 1047 = screen_brightness_nits : 250 nits

If many independent sources assert claim 892, then we might find the graph naturally returning to that region more frequently than others.

However it would be naive to classify each source as independent by default. The problem is that agreement doesn't automatically imply independence; sources tend to just copy other sources.

## Dependency Propagation

![Dependency Propagation](../images/dependency_propagation.png)

In the graph above:

- S1 supports claim C1
- S2 may reference or inherit from S1
- Therefore, C2 may receive reinforcement originating from a partially shared dependency, not truly independent verification.

It may be useful to explore that the structure of the graph might carry some credibility signals.
