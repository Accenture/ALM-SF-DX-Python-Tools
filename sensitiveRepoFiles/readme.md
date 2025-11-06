# ** Sensitive File Search Script Documentation **
---
## **Description**

This Python script searches for sensitive files in a git repository. Sensitive files are files that have certain file extensions, such as __.key, .crt, .pem, etc.__, which are often used to store sensitive information.

The script can search all branches of the repository or just the main branches (release, master, main, develop). For each sensitive file found, the script will record the branches where the file is located and the commits where the file was modified.

## **How to use**

To run the script, you must have Python installed on your system. The script also requires the `argparse, logging and jinja2` modules. You can install these modules using pip:

```python 
pip install argparse logging jinja2 
```

To execute the script, use the following command

```python 
python script.py /path/to/repository
```

Replace /path/to/repository with the path to the git repository you want to search for sensitive files.

If you only want to search the main branches, use the --main\_only argument:

```python 
python script.py /path/to/repository --main\_only 
```

## **Output**

The script generates an HTML file named results.html containing the search results. For each sensitive file found, the HTML file shows the branches in which the file is located and the commits in which the file was modified.

If no sensitive files are found, the script logs a message indicating that no results were found and does not generate the HTML file.

## **Errors and Exceptions**

The script handles several error cases:

- If the path to the repository does not exist, the script logs an error and terminates.
- If the path to the HTML template does not exist, the script logs an error and terminates.
- If an error occurs while executing a git command, the script logs the error but continues to run.

## **Notes**

This script changes the current working directory to the git repository. Note this if you plan to run other commands after this script in the same context.

Also, this script performs a checkout on each branch it examines. This means that any uncommitted changes to your repository will be lost. Make sure you have committed all your changes before running this script.
