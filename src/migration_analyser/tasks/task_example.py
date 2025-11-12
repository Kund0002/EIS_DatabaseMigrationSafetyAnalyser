class StatementDetector:
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return f"statementDetectorResult(info='{self.info}')"


def run_task():
    # do the fuckass detection here
    result = StatementDetector("script is fine")
    return result
