def apply_filters(qs, filters):
    # category label filter
    if filters.get("category"):
        label = filters["category"]
        qs = qs.extra(
            where=["EXISTS (SELECT 1 FROM jsonb_array_elements(cat_path) AS c WHERE c->>'label'=%s)"],
            params=[label]
        )
    # price range
    if filters.get("min_price") is not None:
        qs = qs.extra(
            where=["(price->>'price')::float >= %s"],
            params=[filters["min_price"]]
        )
    if filters.get("max_price") is not None:
        qs = qs.extra(
            where=["(price->>'price')::float <= %s"],
            params=[filters["max_price"]]
        )
    # export only
    if filters.get("export_only"):
        qs = qs.extra(
            where=["(export->>'status')::boolean = true"]
        )
    return qs
