class ConflictEngine:

    def detect(
        self,
        field,
        selected,
        observed
    ):

        unique = []

        for value in observed:
            if value not in unique:
                unique.append(value)

        if len(unique) <= 1:
            return None

        return {
            "field": field,
            "selected": selected,
            "observed": unique,
            "severity": "medium"
        }