# App modules
from testapp.github_info_header import github_info_header

import os
app_data_path = os.getenv("TESTAPP_DATA_PATH")

if app_data_path is None:
    raise Exception("You need to add the path to your data directory to the TESTAPP_DATA_PATH environmental variable!")


can_cd_to_data_path = os.system("cd " + app_data_path)

if can_cd_to_data_path != 0:
    raise Exception("Cannot cd to " + app_data_path +
                    ". Please create the directory or double-check your TESTAPP_DATA_PATH entry.")


