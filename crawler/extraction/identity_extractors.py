def extract_hard_ids(raw_text):
    identities = []

    try:
        raw_text = raw_text or ""

        match = re.search(r'"(?:primary_barcode|gtin12|gtin13|upc)"\s*:\s*"(\d{12,13})"', raw_text)
        if match:
            identities.append(("gtin", match.group(1)))
        else:
            match = re.search(r'\b((?:0|1|6|7|8)\d{11})\b', raw_text)
            if match:
                identities.append(("gtin", match.group(1)))

        dpci_match = re.search(r'\b(\d{3}-\d{2}-\d{4})\b', raw_text)
        if dpci_match:
            identities.append(("dpci", dpci_match.group(1)))

        model_match = re.search(r'"model_number"\s*:\s*"([^"]+)"', raw_text)
        if not model_match:
            model_match = re.search(r'"(?:model|mpn)"\s*:\s*"([^"]+)"', raw_text)

        if model_match:
            identities.append(("model", model_match.group(1)))

        return list(set(identities))

    except Exception as e:
        print(f"[ID EXTRACTION ERROR]: {e}")
        return []


def extract_labeled_ids(markdown):
    identity = {"gtin": None, "model": None}

    patterns = [
        (r"(?:UPC|GTIN|EAN)[^:\n]*[:\-]\s*(\d{12,14})", "gtin"),
        (r"(?:Model(?:\s*Number)?|MPN)[^:\n]*[:\-]\s*([A-Z0-9\-]{4,})", "model"),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, markdown or "", re.IGNORECASE)
        if match:
            val = match.group(1).strip()

            if key == "gtin" and val.isdigit():
                identity["gtin"] = val

            elif key == "model":
                val = val.upper()
                if re.search(r"[A-Z]", val) and re.search(r"\d", val):
                    identity["model"] = val

    return identity


def extract_model_fallback(markdown):
    if not markdown:
        return None

    match = re.search(r"-\s*([A-Z0-9\-]{5,})", markdown)
    if match:
        return match.group(1).upper()

    match = re.search(r"\b([A-Z]{2,}-?[A-Z0-9]{3,})\b", markdown)
    if match:
        return match.group(1).upper()

    return None


def extract_model_from_text(markdown, html):
    text = f"{markdown or ''}\n{html or ''}"

    patterns = [
        r"(?:Model\s*(?:Number|No\.?|#)?|MPN)\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-\/\.]{4,})",
        r'"(?:model|model_number|mpn)"\s*:\s*"([^"]+)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        candidate = match.group(1).strip().upper()

        if is_valid_model(candidate):
            print(f"[MODEL TEXT FOUND] {candidate}")
            return candidate

        print(f"[MODEL TEXT REJECTED] {candidate}")

    return None


def extract_sku_from_text(markdown, html):
    text = f"{markdown or ''}\n{html or ''}"

    match = re.search(
        r"(?:SKU)\s*[:#]?\s*(\d{5,})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None