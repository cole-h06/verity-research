from db import (
    upsert_product,
    upsert_price
)

from search_bridge import (
    run_search_bridge
)

from scout import (
    save_url
)

from brain import (
    clean_price
)


def run_post_identity_enrichment(
    conn,
    existing,
    gtin,
    model,
    sku,
    brand,
    title,
    price,
    image_url,
    category,
    domain,
    url,
    product,
    next_specs
):
    if not (gtin or model):
        return

    if existing:

        product_payload = {
            "model": existing["model"] or model,
            "brand": existing["brand"] or brand,
            "title": existing["title"] or title,
            "price": price,
            "image_url": (
                existing["image_url"]
                or image_url
            ),
            "gtin": gtin
        }

    else:

        product_payload = {
            "model": model,
            "brand": brand,
            "title": title,
            "price": price,
            "image_url": image_url,
            "gtin": gtin
        }

    upsert_product(
        conn,
        product_payload
    )

    structured_identity_found = bool(
        gtin
        or (
            model
            and product
        )
        or (
            next_specs
            and (
                gtin
                or model
            )
        )
    )

    if structured_identity_found:

        print("\n[CASE A] STRUCTURED IDENTITY FOUND")

        print(
            "[POST-IDENTITY SEARCH BRIDGE - "
            "TOP 3 MODE]"
        )

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

    else:

        print("\n[CASE B] NO STRUCTURED IDENTITY")
        print("[SINGLE URL MODE]")

        first_domain_row = conn.execute("""
            SELECT 1
            FROM crawled_pages cp
            JOIN sources s
              ON s.domain = ?
            LIMIT 1
        """, (domain,)).fetchone()

        if not first_domain_row:

            save_url(
                conn,
                url,
                category=category,
                priority=10,
                provider="fallback"
            )

            print(
                f"[SAVED SINGLE FALLBACK URL] "
                f"{url}"
            )

    print("\n=== UPSERT PRODUCT ===")
    print(product_payload)

    cleaned_price = clean_price(price)

    if gtin and cleaned_price:

        print(
            f"[PRICE INSERT] "
            f"{gtin} | "
            f"{cleaned_price} | "
            f"{domain}"
        )

        upsert_price(conn, {
            "gtin": gtin,
            "domain": domain,
            "price": cleaned_price,
            "url": url
        })