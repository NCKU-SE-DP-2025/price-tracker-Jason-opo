class DomainMismatchException(Exception):
    """Raised when a given URL does not belong to the crawler's allowed domain."""

    def __init__(self, url: str, message: str = "URL does not match crawler domain"):
        super().__init__(f"{message}: {url}")
        self.url = url