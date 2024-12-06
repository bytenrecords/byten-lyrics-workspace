import yaml
import glob
import os
import agents.generate_response
from dotenv import load_dotenv

load_dotenv()

def load_config(file_path):
    """
    Load and parse the YAML configuration file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Parsed configuration data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The config file at {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file: {exc}")

def consolidate_output_files_to_variable(workspace_dir):
    """
    Consolidates the content of all `output.txt` files in the workspace subdirectories
    into a single string variable in the specified format.

    Parameters:
        workspace_dir (str): The path to the workspace directory.

    Returns:
        str: The consolidated content as a formatted string.
    """
    # Find all output.txt files in the workspace subdirectories
    pattern = os.path.join(workspace_dir, '*', 'output.txt')
    files = glob.glob(pattern)

    if not files:
        return "No output.txt files found in the workspace subdirectories."

    consolidated_content = []

    for file_path in files:
        try:
            with open(file_path, 'r') as infile:
                content = infile.read()
                consolidated_content.append(f"# {file_path}\n{content}")
        except Exception as e:
            consolidated_content.append(f"# {file_path}\nError reading file: {e}")
    
    return "\n\n".join(consolidated_content)

def create_workspace_folders(config, workspace_dir):
    """
    Creates a folder for each configuration name under the workspace directory.

    Parameters:
        config (dict): Configuration data loaded from the YAML file.
        workspace_dir (str): The base directory for creating workspace folders.
    """
    for key in config:
        folder_path = os.path.join(workspace_dir, key)
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")
        except Exception as e:
            print(f"Error creating folder {folder_path}: {e}")

def main():
    # Path to the config file
    config_path = "agents/config.yml"
    workspace_dir = "workspace"
    
    try:
        # Load the configuration
        config = load_config(config_path)
        print("Configuration loaded successfully!")

        # Iterate over each configuration item
        for config_name, config_content in config.items():
            print(f"\nConfiguration for '{config_name}':")
            print(config_content)

            # Create a folder for the current config in the workspace
            folder_path = os.path.join(workspace_dir, config_name)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")

            # Consolidate output files and print the result
            consolidated_output = consolidate_output_files_to_variable(folder_path)
            print("\nConsolidated Output:\n")
            print(consolidated_output)

            prompt = str(config_content)+consolidated_output

            print(agents.generate_response.generate_response(prompt))

    except Exception as e:
        print(f"Failed to execute: {e}")

if __name__ == "__main__":
    main()
