import wgse.gui
from wgse.utility.check_prerequisites import (CheckPrerequisites)


def main():
    CheckPrerequisites().check_prerequisites()
    wgse.gui.main()
    
if __name__ == "__main__":
    main()