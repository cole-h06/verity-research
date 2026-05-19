def extract_home_depot_specs(spec_payloads):
    all_specs = []

    for payload in spec_payloads:

        try:
            root = payload.get("data", {})

            product_block = (
                root.get("productClientOnlyProduct", {})
                .get("product")
                or root.get("product")
                or {}
            )

            groups = product_block.get(
                "specificationGroup",
                []
            )

            for group in groups:

                for spec in group.get(
                    "specifications",
                    []
                ):

                    name = spec.get("specName")
                    value = spec.get("specValue")

                    if name and value:
                        all_specs.append(
                            (name, value)
                        )

        except:
            pass

    seen = set()

    extracted_specs = []

    for name, value in all_specs:

        key = (
            name.lower(),
            str(value).lower()
        )

        if key not in seen:

            seen.add(key)

            extracted_specs.append(
                (name, value)
            )

    return extracted_specs