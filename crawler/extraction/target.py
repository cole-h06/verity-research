def find_specs(obj):
    results = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            key = k.lower()

            if key == "bundlespecificationdetails" and isinstance(v, list):
                results.extend(v)

            elif key == "specificationgroup" and isinstance(v, list):
                for group in v:
                    if isinstance(group, dict):
                        specs = group.get("specifications", [])
                        if isinstance(specs, list):
                            results.extend(specs)

            else:
                results.extend(find_specs(v))

    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_specs(item))

    return results


def extract_target_specs(data):
    results = []

    try:
        product = data.get("data", {}).get("product", {})
        item = product.get("item", {})
        description = item.get("product_description", {})

        specs = description.get("soft_specifications", {}).get("specifications", [])
        for s in specs:
            label = s.get("label")
            value = s.get("value")
            if label and value:
                results.append((clean_html(label), clean_html(value)))

        bullets = description.get("bullet_descriptions", [])
        for b in bullets:
            if b:
                raw = re.sub(r"<.*?>", "", b).strip()

                if ":" in raw:
                    name, value = raw.split(":", 1)
                    results.append((name.strip(), value.strip()))
                else:
                    clean = clean_html(b)
                    results.append(("feature", clean))

    except Exception as e:
        print(f"[TARGET PARSE ERROR]: {e}")

    if not results:
        def walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key = k.lower()

                    if key in ["soft_specifications", "softspecifications", "bullet_description", "item_attributes", "specifications"]:
                        if isinstance(v, list):
                            for item in v:
                                if isinstance(item, str):
                                    results.append(("feature", clean_html(item)))
                                elif isinstance(item, dict):
                                    name = (
                                        item.get("label")
                                        or item.get("name")
                                        or item.get("specification_name")
                                    )
                                    value = (
                                        item.get("value")
                                        or item.get("definition")
                                        or item.get("specification_value")
                                    )
                                    if name and value:
                                        results.append((clean_html(name), clean_html(value)))

                    walk(v)

            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)

    return list(set(results))


def get_target_tcin(url):
    match = re.search(r"/A-(\d+)", url)
    return match.group(1) if match else None


def get_upc(html):
    try:
        match = re.search(r'"primary_barcode"\s*:\s*"(\d{12,13})"', html or "")

        if not match:
            match = re.search(r'"gtin(?:12|13|14)?"\s*:\s*"(\d{12,14})"', html or "")

        if not match:
            match = re.search(r'"upc"\s*:\s*"(\d{12,13})"', html or "")

        if match:
            upc = match.group(1)
            print(f"[HTML UPC FOUND]: {upc}")
            return upc

    except Exception as e:
        print(f"[HTML UPC ERROR]: {e}")

    return None


def get_target_specs_direct(url):
    tcin = get_target_tcin(url)
    if not tcin:
        print("[TARGET API ERROR]: Could not extract TCIN from URL")
        return []

    params = {
        "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
        "tcin": tcin,
        "store_id": "3991",
        "pricing_store_id": "3991",
        "has_pricing_store_id": "true",
        "is_bot": "false"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.target.com/",
        "Origin": "https://www.target.com"
    }

    try:
        response = requests.get(
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1",
            params=params,
            headers=headers,
            timeout=20
        )

        data = response.json()

        product_data = data.get("data", {}).get("product", {})
        item = product_data.get("item", {})
        desc = item.get("product_description", {})
        price_info = product_data.get("price", {})

        title = desc.get("title")
        brand = (
            item.get("primary_brand", {}).get("name")
            or item.get("product_brand", {}).get("name")
        )
        price = price_info.get("current_retail")
        image = (
            item.get("enrichment", {}).get("images", {}).get("primary_image_url")
            or item.get("images", {}).get("primary_image_url")
        )
        model = desc.get("model_number")

        product_item = product_data.get("item", {})
        upc = product_item.get("primary_barcode")

        next_specs = extract_target_specs(data)

        if upc:
            upc = normalize_gtin(upc)
            print(f"[FOUND UPC]: {upc}")
            next_specs.append(("gtin", upc))

        if not upc:
            try:
                html_headers = {
                    "User-Agent": headers["User-Agent"],
                    "Accept": "text/html",
                    "Referer": "https://www.target.com/"
                }

                html_resp = requests.get(url, headers=html_headers, timeout=20)
                html_upc = get_upc(html_resp.text)

                if html_upc:
                    html_upc = normalize_gtin(html_upc)
                    print(f"[FOUND HTML UPC]: {html_upc}")
                    next_specs.append(("gtin", html_upc))

            except Exception as e:
                print(f"[TARGET HTML UPC ERROR]: {e}")

        if title:
            next_specs.append(("title", title))

        if brand:
            next_specs.append(("brand", brand))

        if price:
            next_specs.append(("price", price))

        if image:
            next_specs.append(("image_url", image))

        if model:
            next_specs.append(("model", model))

        return next_specs

    except Exception as e:
        print(f"[TARGET API ERROR]: {e}")
        return []