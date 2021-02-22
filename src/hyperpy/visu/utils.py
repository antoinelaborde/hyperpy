import os
import pathlib


def figure_script():
    """
    return the absolute path of the figure_script folder and the list of all figure script available
    """

    path = os.path.join(pathlib.Path(__file__).parent.absolute(), "figure_script")
    figure_files = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    ]
    figure_files.remove("__init__.py")
    return path, figure_files


def check_figure_file(figure_file_name):
    """
    check if figure_file_name is available

    figure_file_name: str, figure file name.

    path: path to the figure script
    """
    path, fig_files = figure_script()
    fig_files_no_ext = [filename.replace(".py", "") for filename in fig_files]
    if figure_file_name in fig_files_no_ext:
        return os.path.join(path, figure_file_name + ".py")
    else:
        return None
