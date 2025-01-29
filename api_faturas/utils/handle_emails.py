class HandleEmails:
    def __init__(self):
        self.emails = []

    def extract_from_dict(self, data: dict, search_key: str) -> list[str]:
        """
        Extract the emails from a dictionary and add them to the list.

        Args:
            data (dict): Dictionary with the emails to be extracted.
            search_key (str): Key to be searched in the dictionary.
        """
        for key, value in data.items():
            if key.startswith(search_key) and value.strip():
                self.emails.extend(
                    email.strip() for email in value.split(';') if email.strip()
                )

        return self.emails
