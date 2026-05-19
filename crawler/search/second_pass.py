from search_bridge import run_search_bridge

from db import mark_complete

from identity.gtin import (
    normalize_gtin
)


def run_second_pass_discovery(
    conn,
    gtin,
    model,
    sku,
    brand,
    title,
    price,
    image_url,
    category,
    url
):
    print(
        "[RESOLVED AFTER UNRESOLVED] "
        "marking complete"
    )

    print("[SEARCH BRIDGE INPUT]", {
        "gtin": gtin,
        "model": model,
        "sku": sku,
        "brand": brand,
        "title": title
    })

    before_gtin = gtin
    before_model = model

    run_search_bridge(conn, {
        "gtin": gtin,
        "model": model,
        "sku": sku,
        "brand": brand,
        "title": title,
        "price": price,
        "image_url": image_url,
        "category": category
    })

    refreshed = conn.execute("""
        SELECT gtin, model
        FROM products
        WHERE
            (gtin IS NOT NULL AND gtin = ?)
            OR (
                model IS NOT NULL
                AND lower(model) = lower(?)
            )
        LIMIT 1
    """, (
        gtin or "",
        model or ""
    )).fetchone()

    if refreshed:

        new_gtin = normalize_gtin(
            refreshed["gtin"]
        )

        new_model = refreshed["model"]

        gained_gtin = (
            not before_gtin
            and new_gtin
        )

        gained_model = (
            not before_model
            and new_model
        )

        if gained_gtin or gained_model:

            print(
                "[SECOND SEARCH BRIDGE PASS]"
            )

            print("gtin:", new_gtin)
            print("model:", new_model)

            run_search_bridge(conn, {
                "gtin": new_gtin,
                "model": new_model,
                "sku": sku,
                "brand": brand,
                "title": title,
                "price": price,
                "image_url": image_url,
                "category": category
            })

    mark_complete(conn, url)

    return {
        "gtin": gtin,
        "model": model,
        "needs_enrichment": False,
        "claims_found": 0
    }