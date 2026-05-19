from extraction.jsonld import (
    extract_product_nodes,
    extract_json_ld_from_html
)

from brain import clean_price


def find_product(obj):
    if isinstance(obj, dict):

        t = obj.get("@type")

        if t == "Product" or (
            isinstance(t, list)
            and "Product" in t
        ):
            return obj

        for v in obj.values():
            result = find_product(v)

            if result:
                return result

    elif isinstance(obj, list):

        for item in obj:
            result = find_product(item)

            if result:
                return result

    return None


def extract_product_data(
    html,
    extracted_specs,
    next_specs,
    generic_specs,
    result=None,
    url=None
):
    json_ld = extract_json_ld_from_html(html)

    product = find_product(json_ld)

    if product:

        products = extract_product_nodes(json_ld)

        for p in products:

            if (
                isinstance(p, dict)
                and p.get("additionalProperty")
            ):
                product = p
                break

    print("\n=== JSON-LD DEBUG ===")
    print("Product found:", bool(product))

    if product:
        print("Keys:", list(product.keys())[:10])

        print(
            "Has additionalProperty:",
            "additionalProperty" in product
        )

        print(
            "Count:",
            len(product.get("additionalProperty", []))
        )

    print("\n===== STATUS =====")

    print(
        "Success:",
        result.success if result else False
    )

    print(
        "Status Code:",
        result.status_code if result else None
    )

    print(
        "Final URL:",
        result.url if result else url
    )

    gtin = None
    sku = None
    model = None
    title = None
    brand = None
    price = None
    image_url = None

    if product:

        title = product.get("name")

        if isinstance(product.get("brand"), dict):

            brand = product.get(
                "brand",
                {}
            ).get("name")

        else:
            brand = product.get("brand")

        gtin = (
            product.get("gtin13")
            or product.get("gtin12")
            or product.get("gtin14")
            or product.get("gtin")
            or product.get("upc")
        )

        if gtin is not None:
            gtin = str(gtin).replace(".0", "")

        sku = product.get("sku")

        model = (
            product.get("model")
            or product.get("mpn")
        )

        offers = product.get("offers")

        if isinstance(offers, list) and offers:
            offers = offers[0]

        if isinstance(offers, dict):
            price = clean_price(
                offers.get("price")
            )

        img = product.get("image")

        if (
            isinstance(img, list)
            and len(img) > 0
        ):
            image_url = img[0]

        elif isinstance(img, str):
            image_url = img

    if next_specs or extracted_specs:
        print(
            "[STRUCTURED SPECS FOUND - "
            "SKIPPING GENERIC HTML]"
        )

    if (
        product
        and product.get("additionalProperty")
    ):

        print(
            "[SKIPPING GENERIC HTML SPECS - "
            "JSON-LD additionalProperty present]"
        )

        combined_specs = (
            extracted_specs
            + next_specs
        )

    else:

        combined_specs = (
            extracted_specs
            + next_specs
            + generic_specs
        )

    return {
        "json_ld": json_ld,
        "product": product,
        "combined_specs": combined_specs,
        "title": title,
        "brand": brand,
        "gtin": gtin,
        "sku": sku,
        "model": model,
        "price": price,
        "image_url": image_url
    }