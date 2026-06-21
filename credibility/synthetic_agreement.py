# synthetic_agreement.py

import random

from collections import defaultdict


# we start every source equally
# so any ranking differences must
# emerge from the graph itself
def initialize_uniform(source_ids):

    n = len(source_ids)

    return {
        source_id: 1.0 / n
        for source_id in source_ids
    }


# random initialization helps us
# verify whether the verifier is
# converging to the same solution
def initialize_random(source_ids):

    scores = {
        source_id: random.random()
        for source_id in source_ids
    }

    return normalize(
        scores
    )


# agreement is the entire point of
# this experiment
#
# we are intentionally creating
# synthetic graphs where we know
# exactly how much agreement exists
#
# if agreement matters, the verifier
# should react accordingly
def build_agreement_scores():

    return {
        "X": 1.00,   # everyone agrees
        "Y": 0.50    # disagreement
    }


# credibility flows from sources
# into claims
#
# agreement scales how much support
# a claim receives
def score_claims(
    credibility,
    claim_to_sources,
    source_to_claims,
    agreement_scores
):

    claim_support = {}

    for claim_id, source_ids in claim_to_sources.items():

        support = 0.0

        for source_id in source_ids:

            degree = len(
                source_to_claims[source_id]
            )

            if degree == 0:
                continue

            support += (
                credibility[source_id]
                / degree
            )

        claim_support[claim_id] = (
            support *
            agreement_scores.get(
                claim_id,
                1.0
            )
        )

    return claim_support


# claims push support back
# into their attached sources
def update_sources(
    claim_support,
    source_to_claims
):

    next_credibility = {}

    for source_id, claim_ids in source_to_claims.items():

        support_sum = 0.0

        for claim_id in claim_ids:

            support_sum += (
                claim_support[claim_id]
            )

        next_credibility[source_id] = (
            support_sum
        )

    return next_credibility


def normalize(scores):

    total = sum(
        scores.values()
    )

    if total == 0:
        return scores

    return {
        node: value / total
        for node, value
        in scores.items()
    }


# we repeatedly propagate until
# the credibility vector stops
# changing
#
# if agreement actually matters,
# the agreed-upon cluster should
# pull ahead over time
def run_until_convergence(
    source_to_claims,
    claim_to_sources,
    agreement_scores,
    credibility,
    tolerance=1e-8,
    max_iterations=1000
):

    iteration = 0

    while iteration < max_iterations:

        previous = credibility.copy()

        claim_support = score_claims(
            credibility,
            claim_to_sources,
            source_to_claims,
            agreement_scores
        )

        credibility = update_sources(
            claim_support,
            source_to_claims
        )

        credibility = normalize(
            credibility
        )

        maximum_difference = 0.0

        for source_id in credibility:

            difference = abs(
                credibility[source_id]
                - previous[source_id]
            )

            if difference > maximum_difference:

                maximum_difference = (
                    difference
                )

        print(
            f"iteration {iteration + 1:>3}   "
            f"delta = "
            f"{maximum_difference:.12f}"
        )

        if maximum_difference < tolerance:

            print()
            print(
                f"converged after "
                f"{iteration + 1} "
                f"iterations"
            )

            return credibility

        iteration += 1

    return credibility


# if agreement influences
# propagation, A and B should
# eventually be able to outrank C
def build_graph():

    source_to_claims = defaultdict(set)

    claim_to_sources = defaultdict(set)

    source_to_claims["A"].add("X")
    source_to_claims["B"].add("X")
    source_to_claims["C"].add("Y")

    claim_to_sources["X"].update(
        ["A", "B"]
    )

    claim_to_sources["Y"].add(
        "C"
    )

    return (
        source_to_claims,
        claim_to_sources
    )


def print_rankings(scores):

    print()
    print("final rankings")
    print("--------------")

    for source_id, score in sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{source_id:<10}"
            f"{score:.8f}"
        )

    print()


def main():

    print()
    print("building synthetic graph...")

    (
        source_to_claims,
        claim_to_sources
    ) = build_graph()

    agreement_scores = (
        build_agreement_scores()
    )

    print(
        f"sources: "
        f"{len(source_to_claims)}"
    )

    print(
        f"claims: "
        f"{len(claim_to_sources)}"
    )

    print()

    source_ids = list(
        source_to_claims.keys()
    )

    credibility = (
        initialize_uniform(
            source_ids
        )
    )

    credibility = (
        run_until_convergence(
            source_to_claims,
            claim_to_sources,
            agreement_scores,
            credibility
        )
    )

    print_rankings(
        credibility
    )


if __name__ == "__main__":
    main()