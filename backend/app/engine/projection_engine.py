from copy import deepcopy


class ProjectionEngine:
    """
    Projects one or many canonical candidates.

    Backward compatible:
        project(candidate)

    New:
        project_many(candidates)
    """

    def project(self, candidate, config=None):

        config = config or {}

        result = deepcopy(candidate.to_dict())

        self._apply_field_selection(result, config)
        self._apply_field_renaming(result, config)
        self._apply_confidence(result, config)
        self._apply_provenance(result, config)
        self._apply_conflicts(result, config)
        self._apply_missing_policy(result, config)

        return result

    # ---------------- NEW ---------------- #

    def project_many(self, candidates, config=None):

        config = config or {}

        projected = [
            self.project(candidate, config)
            for candidate in candidates
        ]

        return {
            "candidate_count": len(projected),
            "candidates": projected
        }

    

    def _apply_field_selection(self, result, config):

        fields = config.get("fields")

        if not fields:
            return

        keep = set(fields)

        for key in list(result.keys()):

            if key not in keep:
                result.pop(key)

    # ------------------------------------------

    def _apply_field_renaming(self, result, config):

        rename = config.get("rename", {})

        for old, new in rename.items():

            if old in result:

                result[new] = result.pop(old)

    # ------------------------------------------

    def _apply_confidence(self, result, config):

        include = config.get(
            "include_confidence",
            True
        )

        if not include:
            result.pop("confidence", None)

    # ------------------------------------------

    def _apply_provenance(self, result, config):

        include = config.get(
            "include_provenance",
            True
        )

        if not include:
            result.pop("provenance", None)

    # ------------------------------------------

    def _apply_conflicts(self, result, config):

        include = config.get(
            "include_conflicts",
            True
        )

        if not include:
            result.pop("conflicts", None)

    # ------------------------------------------

    def _apply_missing_policy(self, result, config):

        policy = config.get(
            "missing_policy",
            "keep"
        )

        if policy == "keep":
            return

        if policy == "omit":

            for key in list(result.keys()):

                if result[key] in (
                    "",
                    [],
                    {},
                    None
                ):

                    result.pop(key)

        elif policy == "null":

            for key, value in result.items():

                if self._is_missing(value):
                    result[key] = None

    def _is_missing(self, value):

        if value in ("", None):
            return True

        if isinstance(value, (list, tuple, set)) and len(value) == 0:
            return True

        if isinstance(value, dict):
            if len(value) == 0:
                return True
            return all(self._is_missing(v) for v in value.values())

        return False