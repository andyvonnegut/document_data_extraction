pip install requirements & brew install poppler

To use this tool;

1) Configure document types in GPT Functions/GPT_Functions.csv.  Add an OpenAI API Key
2) Configure data elements to be extracted in GPT Functions/GPT_Function_Parameters.csv
3) Place documents to be reviewed in Test_Data/Function_Name where Function_Name = the name of the function defined in GPT Functions/GPT_Functions.csv
4) Run the tool
5) Output will be written to a .csv file in Output/Function_Name where Function_Name = the name of the function defined in GPT Functions/GPT_Functions.csv
