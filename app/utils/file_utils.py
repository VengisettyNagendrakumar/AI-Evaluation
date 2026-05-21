from pathlib import Path


class FileUtils:

    @staticmethod
    def get_extension(
        file_path: str
    ) -> str:

        return Path(
            file_path
        ).suffix.lower()

    @staticmethod
    def file_exists(
        file_path: str
    ) -> bool:

        return Path(
            file_path
        ).exists()

    @staticmethod
    def create_directory(
        directory_path: str
    ):

        Path(
            directory_path
        ).mkdir(
            parents=True,
            exist_ok=True
        )