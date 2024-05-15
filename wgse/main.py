import wgse.gui
from wgse.utility.check_prerequisites import (CheckPrerequisites,
                                              PrerequisiteIssueType)


def main():
    failing = CheckPrerequisites().check_prerequisites()
    if len(failing) > 0:
        cfg_info = [x for x in failing if x.type == PrerequisiteIssueType.CONFIG_ISSUE]
        cfg_warn = [x for x in failing if x.type == PrerequisiteIssueType.CONFIG_ISSUE]
        bin_error = [x for x in failing if x.type == PrerequisiteIssueType.BINARY_ERROR]
        cfg_error = [x for x in failing if x.type == PrerequisiteIssueType.CONFIG_ISSUE]
        bin_missing = [x for x in failing if x.type == PrerequisiteIssueType.MISSING_BINARY]
    wgse.gui.main()
    
if __name__ == "__main__":
    main()