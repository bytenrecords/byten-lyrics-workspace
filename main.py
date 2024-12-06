import yaml
import glob
import os
import agents.generate_response
from dotenv import load_dotenv
import subprocess
import shutil
import re

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
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        print("Configuration loaded successfully!")

        # Iterate over each configuration item
        for config_name, config_content in config.items():
            print(f"\nConfiguration for '{config_name}':")
            print(config_content)

            # Extract committer details from config
            committer_name = config_content.get('name', 'Default Committer')
            committer_email = config_content.get('email', 'default@example.com')

            # Create a folder for the current config in the workspace
            folder_path = os.path.join(workspace_dir, config_name)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")

            # Generate the prompt by combining config content and consolidated output
            consolidated_output = consolidate_output_files_to_variable('workspace')
            prompt = str(config_content) + "context:\n" + consolidated_output

            # Generate the response
            response = agents.generate_response.generate_response(prompt)
            print("\nGenerated Response:\n")
            print(response)

            # Save the response to output.txt in the corresponding workspace folder
            output_file_path = os.path.join(folder_path, 'output.txt')
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(response)
            print(f"Response saved to: {output_file_path}")

            # Infer the commit message (first 50 characters of response)
            commit_message = response[:50]

            # Git commit
            try:
                subprocess.run(["git", "add", output_file_path], check=True)
                subprocess.run(
                    ["git", "-c", f"user.name={committer_name}", "-c", f"user.email={committer_email}",
                     "commit", "-m", commit_message],
                    check=True
                )
                print(f"Committed changes for {config_name} with message: '{commit_message}'")
            except subprocess.CalledProcessError as e:
                print(f"Error during git commit: {e}")

            # Special handling for 'byten' configuration
            if config_name == "byten":
                # Remove all punctuation from the filename, leaving only alphanumeric, dashes, and underscores
                sanitized_filename = re.sub(r'[^\w-]', '', response[:50])
                output_copy_path = os.path.join("./output", f"{sanitized_filename}.txt")

                # Ensure the output directory exists
                os.makedirs(os.path.dirname(output_copy_path), exist_ok=True)
                
                # Copy the file
                shutil.copy(output_file_path, output_copy_path)
                print(f"Copied output to: {output_copy_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
