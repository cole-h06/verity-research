def extract_walmart_specs(data):
    results = []

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = k.lower()

                if key in ["specifications", "attributes", "allattributes", "idml"]:
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                name = (
                                    item.get("name")
                                    or item.get("specName")
                                    or item.get("attributeName")
                                )
                                value = (
                                    item.get("value")
                                    or item.get("specValue")
                                    or item.get("attributeValue")
                                )

                                if name and value:
                                    results.append((name, value))

                walk(v)

        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return list(set(results))