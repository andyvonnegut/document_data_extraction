pip install requirements & brew install poppler or see below to install Poppler on Windows / Linux

To use this tool;

1) Configure document types in GPT Functions/GPT_Functions.csv.  Add an OpenAI API Key
2) Configure data elements to be extracted in GPT Functions/GPT_Function_Parameters.csv
3) Place documents to be reviewed in Test_Data/Function_Name where Function_Name = the name of the function defined in GPT Functions/GPT_Functions.csv
4) Run the tool
5) Output will be written to a .csv file in Output/Function_Name where Function_Name = the name of the function defined in GPT Functions/GPT_Functions.csv

The library pdf2image requires the Poppler library, which isn't available via PIP.

Installation Instructions

Install Poppler on macOS (using Homebrew):
    You can install Poppler with the following command:
    brew install poppler

Install Poppler on Ubuntu/Linux:

    On Ubuntu or other Debian-based systems, you can install it with:
    sudo apt-get install poppler-utils

Install Poppler on Windows:

    For Windows, you typically download pre-built binaries. You can download it from this 
    GitHub repository, extract it, and then add the bin/ directory to your system's PATH.
    https://github.com/oschwartz10612/poppler-windows/releases/