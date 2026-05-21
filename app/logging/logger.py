import logging

from pathlib import Path

from logging.handlers import (
    RotatingFileHandler
)

from app.config.settings import (
    settings
)

from app.logging.formatter import (
    CustomFormatter
)



logging.basicConfig(
    level=getattr(
        logging,
        settings.LOG_LEVEL.upper(),
        logging.INFO
    )
)


def get_logger(
    logger_name: str
):

    logger = logging.getLogger(
        logger_name
    )

   

    if logger.handlers:

        return logger



    log_level = getattr(
        logging,
        settings.LOG_LEVEL.upper(),
        logging.INFO
    )

    logger.setLevel(
        log_level
    )



    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setLevel(
        log_level
    )

    console_handler.setFormatter(
        CustomFormatter()
    )

    logger.addHandler(
        console_handler
    )

 

    if settings.LOG_TO_FILE:

        try:

            log_file = Path(
                settings.LOG_FILE
            )

            log_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            file_handler = (
                RotatingFileHandler(

                    filename=log_file,

                    maxBytes=(
                        10 * 1024 * 1024
                    ),

                    backupCount=5,

                    encoding="utf-8"
                )
            )

            file_handler.setLevel(
                log_level
            )

            file_handler.setFormatter(
                CustomFormatter()
            )

            logger.addHandler(
                file_handler
            )

        except PermissionError:

            print(
                (
                    "WARNING: "
                    "File logging disabled "
                    "because log file "
                    "is not writable."
                )
            )


    logger.propagate =  True

    return logger