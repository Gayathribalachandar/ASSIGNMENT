from rapidfuzz import fuzz


class DeduplicationProcessor:

    @staticmethod
    def deduplicate(values):

        unique = []

        for value in values:

            if not value:
                continue

            duplicate = False

            for existing in unique:

                similarity = fuzz.ratio(

                    value.lower(),

                    existing.lower()

                )

                if similarity >= 90:

                    duplicate = True

                    break

            if not duplicate:

                unique.append(value)

        return unique