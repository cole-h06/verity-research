def extract_product_nodes(json_ld):
    results = []

    def walk(obj):
        if isinstance(obj, dict):
            t = obj.get("@type")

            if t == "Product" or (isinstance(t, list) and "Product" in t):
                results.append(obj)

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(json_ld)
    return results


def extract_json_ld_from_html(html):
    matches = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html or "",
        re.DOTALL | re.IGNORECASE
    )

    for match in matches:
        try:
            parsed = json.loads(match.strip())
        except Exception:
            continue

        products = extract_product_nodes(parsed)
        if products:
            return parsed

    return {}


def extract_json_ld_claims(product):
    claims = []

    if not product:
        return claims

    name = product.get("name")
    if name:
        claims.append(("product_name", name))

    brand = product.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name")
    if brand:
        claims.append(("brand", brand))

    model = product.get("model") or product.get("mpn")
    if model:
        claims.append(("model", model))

    sku = product.get("sku")
    if sku:
        claims.append(("sku", sku))

    color = product.get("color")
    if color:
        claims.append(("color", color))

    for prop in product.get("additionalProperty", []):
        if not isinstance(prop, dict):
            continue
        prop_name = prop.get("name")
        prop_value = prop.get("value")
        if prop_name and prop_value:
            claims.append((prop_name, prop_value))

    return claims