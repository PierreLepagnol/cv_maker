"""
Configuration and data loading utilities.
"""

import json
from pathlib import Path

def load_config(config_path):
    """
    Load configuration JSON file.

    Args:
        config_path: Path to config file

    Returns:
        Dict with configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_data(base_dir='data'):
    """
    Load all JSON data files from data directory.

    Args:
        base_dir: Base directory containing JSON files

    Returns:
        Dict with keys: contact, skills, experience, education, papers, activities, objective
        Missing files return empty dict/list as appropriate
    """
    base_path = Path(base_dir)
    data = {}

    data_files = [
        'contact', 'skills', 'experience', 'education',
        'papers', 'activities', 'objective'
    ]

    for file_name in data_files:
        file_path = base_path / f"{file_name}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data[file_name] = json.load(f)
        else:
            # Provide sensible defaults for missing files
            if file_name in ['skills', 'experience', 'education', 'papers', 'activities']:
                data[file_name] = {file_name: []}
            elif file_name == 'contact':
                data[file_name] = {}
            elif file_name == 'objective':
                data[file_name] = {'text': ''}

    return data
