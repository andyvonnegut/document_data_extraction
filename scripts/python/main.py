import pandas as pd
import os
import requests
import base64
from pdf2image import convert_from_path
import io
import json
import csv

# Get the base directory of the current script
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Construct relative paths for the CSV files
file_path_functions = os.path.join(base_dir, 'GPT Functions', 'GPT_Functions.csv')
file_path_parameters = os.path.join(base_dir, 'GPT Functions', 'GPT_Function_Parameters.csv')

# Load the CSV files
df_functions = pd.read_csv(file_path_functions)
df_parameters = pd.read_csv(file_path_parameters)

# Display available functions to the user
print("Available Functions:")
for idx, function_name in enumerate(df_functions['Function_Name']):
    print(f"{idx + 1}. {function_name}")

# User selects a function
user_choice = int(input("Select the function by entering the corresponding number: ")) - 1

# Ensure the choice is valid
if 0 <= user_choice < len(df_functions):
    selected_function = df_functions.iloc[user_choice]
    
    # Retrieve information for the selected function
    function_name = selected_function['Function_Name']
    api_key = selected_function['API_Key']
    endpoint = selected_function['Endpoint']
    model = selected_function['Model']
    description = selected_function['Description']

    print(f"\nYou selected: {function_name}")
    print(f"API Key: {api_key}")
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model}")
    print(f"Description: {description}")

    # Format the function name to be compatible with API requirements
    formatted_function_name = function_name.replace(" ", "_")

    # Find the corresponding parameters in GPT_Function_Parameters.csv using GPT_Function_Parent
    parameters_for_function = df_parameters[df_parameters['GPT_Function_Parent'] == function_name]

    if not parameters_for_function.empty:
        print("\nParameters for the selected function:")
        print(parameters_for_function.to_string(index=False))
    else:
        print("\nNo parameters found for the selected function.")
        exit(1)  # Exit if no parameters are found

    # Convert the parameters to the required format for the API request using corrected column names
    parameter_properties = {}
    for param in parameters_for_function.to_dict('records'):
        param_def = {
            "type": param['Paremeter_Type'],
            "description": param['Parameter_Description']
        }
        # Add enum if it exists
        if pd.notna(param['Parameter_Enums']):
            param_def["enum"] = eval(param['Parameter_Enums'])
        parameter_properties[param['GPT_Function_Parameter_Name']] = param_def

    # Determine which parameters are required based on the new column
    required_parameters = parameters_for_function[
        parameters_for_function['Required'] == "Yes"
    ]['GPT_Function_Parameter_Name'].tolist()

else:
    print("Invalid selection. Please run the script again and select a valid function.")
    exit(1)

def pdf_to_base64_images(filepath):
    """Converts the first 5 pages of a PDF file to a list of base64-encoded images."""
    images = convert_from_path(filepath, first_page=1, last_page=5)
    base64_images = []
    for image in images:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_images.append(f"data:image/jpeg;base64,{img_str}")
    return base64_images

def write_json_to_csv(json_data, csv_path, filename):
    """Writes the JSON data to the CSV file with fields as headers in one row and values below them."""
    # Check if the file exists
    file_exists = os.path.isfile(csv_path)

    # Open the CSV file in append mode
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(json_data.keys()) + ["Source File"])
        
        # Write headers if the file is new
        if not file_exists:
            writer.writeheader()
        
        # Write the data
        row = json_data.copy()
        row["Source File"] = filename
        writer.writerow(row)

def process_single_pdf(file_path, csv_path):
    """Processes a single PDF file and writes the extracted data to the CSV file."""
    print(f"Processing {file_path}")
    
    # Convert the PDF to base64 images
    base64_images = pdf_to_base64_images(file_path)
    
    # Prepare the API request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    message_content = [
        {
            "type": "text",
            "text": "Extract the data from these images in JSON format defined by the Data_Extraction function."
        }
    ] + [
        {
            "type": "image_url",
            "image_url": {
                "url": img
            }
        } for img in base64_images
    ]

    data = {
        "model": model,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON."
            },
            {
                "role": "user",
                "content": message_content
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": formatted_function_name,  # Use formatted function name
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": parameter_properties,
                        "required": required_parameters
                    }
                }
            }
        ],
        "max_tokens": 4096
    }

    response = requests.post(endpoint, headers=headers, json=data)
    
    print('Status Code:', response.status_code)
    print('Response Body:', response.text)
    
    if response.status_code == 200:
        response_json = response.json()

        # Check if the response contains 'choices' and 'tool_calls'
        if 'choices' in response_json and len(response_json['choices']) > 0:
            tool_calls = response_json['choices'][0]['message'].get('tool_calls', [])
            
            if tool_calls:
                # Extract the arguments string from the tool calls
                arguments_str = tool_calls[0]['function']['arguments']

                # Convert the arguments string to a dictionary
                extracted_data = json.loads(arguments_str)

                # Check if the extracted data is empty
                if extracted_data:
                    # Write the extracted data to CSV
                    write_json_to_csv(extracted_data, csv_path, os.path.basename(file_path))
                else:
                    print(f"No data extracted for {file_path}")
            else:
                print('No tool calls found in the response.')
        else:
            print('No choices found in the response or response format is incorrect.')
    else:
        print('Error:', response.status_code, response.text)

def process_directory(directory_path, csv_path):
    """Processes all PDF files in the given directory."""
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            process_single_pdf(file_path, csv_path)

# Define the relative directory path for the PDFs and the CSV file path
pdf_directory_path = os.path.join(base_dir, 'Test_Data', formatted_function_name)
csv_file_path = os.path.join(base_dir, 'Output', f'{formatted_function_name}.csv')

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

# Process all PDFs in the directory
process_directory(pdf_directory_path, csv_file_path)

print(f"Processing complete. Results saved to {csv_file_path}")