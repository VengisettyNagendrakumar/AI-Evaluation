import logging


class CustomFormatter(
    logging.Formatter
):

    FORMAT = (
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    def format(
        self,
        record
    ):

        formatter = logging.Formatter(
            self.FORMAT
        )

        return formatter.format(
            record
        )