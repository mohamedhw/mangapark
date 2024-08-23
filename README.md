# SC-mangapark

## Overview

This project requires Python and `pip` for managing dependencies. This guide will walk you through setting up a Python virtual environment and installing the required packages.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Setup Instructions

Follow these steps to set up the Python virtual environment and install the required dependencies:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/mohamedhw/mangapark
   cd mangapark
   ```

2. **Create venv**

    ```bash
     python -m venv env
    ```

3.  **Activate the venv**
     - On macOS and Linux:

         ```bash
         source env/bin/activate
         ```
     - On Windows:

         ```bash
         .\env\Scripts\activate
         ```

4.  **Install the requirements**
    ```bash
     pip install -r requirements.txt
    ```

5. **Clean**
    - On macOS and Linux:

    ```bash
    rm -rf .git
    ```

    - On Windows:
        - Command Prompt:
        ```bash
        rmdir /s /q .git
        ```
        - PowerShell:
        ```bash
        Remove-Item -Recurse -Force .git
        ```

## Run the script

1.  **Activate the venv**
     - On macOS and Linux:

         ```bash
         source env/bin/activate
         python main.py
         ```
     - On Windows:

         ```bash
         .\env\Scripts\activate
         python main.py
         ```

