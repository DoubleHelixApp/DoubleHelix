import sentry_sdk

import helix.gui
from helix.utility.check_prerequisites import CheckPrerequisites


def main():
    sentry_sdk.init(
        dsn="https://7942f481884f55dfc85350ef336b3299@o4507282907856896.ingest.de.sentry.io/4507282933874768",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    CheckPrerequisites().check_prerequisites()
    helix.gui.main()


if __name__ == "__main__":
    main()
