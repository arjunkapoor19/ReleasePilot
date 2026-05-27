import subprocess


class GitParser:
    @staticmethod
    def get_diff():
        try:
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    "main...HEAD"
                ],
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout

        except subprocess.CalledProcessError as error:
            print(
                "Failed to retrieve git diff:"
            )

            print(error)

            return ""