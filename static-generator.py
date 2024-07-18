#!/usr/bin/env python
"""Generates static files for the challenges based on their configurations. 
The generated challenges are saved in the 'build' directory."""
import subprocess
import os
from typing import Optional, Dict
import shutil
import yaml #pylint: disable=import-error
from jinja2 import Environment, FileSystemLoader #pylint: disable=import-error

def clean_build_directory(build_path: str) -> None:
    """
    Cleans the build directory by removing its contents.

    :param build_path: The path to the build directory.
    """
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path, exist_ok=True)

def dummy_url_for_with_sub_path(sub_path):
    def dummy_url_for(endpoint: str, path: str) -> str:
        """
        Dummy 'url_for' function to mimic URL generation in templates.
        """
        if not 'static' in endpoint :
            raise InvalidEndpointError(f"Invalid endpoint '{endpoint}' used in dummy_url_for.")

        return "{{ url_for('"+endpoint+ "_" + sub_path +"', path='"+path+"') }}"
    return dummy_url_for

def render_template(template_path: str, context: Dict[str, str]) -> str:
    """
    Renders a template with the given context.

    :param template_path: Path to the template file.
    :param context: A dictionary of context variables for the template.
    :return: Rendered template as a string.
    """
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)
    context['url_for'] = dummy_url_for_with_sub_path(context["sub_path"])  # Add the dummy 'url_for' to the context
    return template.render(context)

def generate_challenge(current_config: Dict, next_config: Optional[Dict], config_dir: str, index: int, path: Optional[str]) -> None:
    """
    Generates a challenge based on the given configuration.
    Renders and saves CSS and JavaScript files using templates, and copies the HTML template file.
    Generates a flag based on the next challenge's template and the current index.

    :param current_config: Dictionary containing the current challenge configuration.
    :param next_config: Optional dictionary containing the next challenge configuration.
    :param index: Index of the current challenge.
    :param config_dir: Directory path of the current challenge configuration.
    :param build_dir: Directory path where the build files should be saved.
    :param path: Path of the challenge.
    """
    # Generate flag based on the next challenge's template, prefixed with the next index
    flag = f"{index + 1}_{next_config['template']}" if next_config \
            and "template" in next_config else ''
    name = f"{index}_{current_config['template']}"

    # Execute the encoding script if specified
    if "encoding_script" in current_config:
        result = subprocess.run(
            [os.path.join(config_dir, current_config["encoding_script"]), flag],
            capture_output=True,
            text=True,
            check=True
        )
        flag = result.stdout.strip()

    first_path_chall_config = [valeurs[0] for cle,valeurs in PATHS["PATHS"].items()]
    first_path_chall_list=[]

    for config_file in first_path_chall_config:
        # add the first challs of each path to the list in order that
        # the end of the INITIAL challenge can redirect to the first challenge of each path
        with open(config_file,'r',encoding='utf-8') as config:
            config=yaml.safe_load(config)
        first_path_chall_list.append(f"{len(PATHS['INITIAL'])}_{config['template']}")

    # Prepare context for rendering templates
    context = {"flag": flag, "chall_name": name, "user_agent": "{{user_agent}}",
                "target_name": "MICHELIN", "display_name":"Michelin", "data": "{{data}}",
                "sub_path": path or "initial", "PATH": PATHS, 
                "first_path_chall":first_path_chall_list, "image":"{{image}}"}

    # Render and save CSS file
    css_content = render_template(os.path.join(config_dir, current_config["css"]), context)
    css_output_path = os.path.join(BUILD_DIR, path, current_config["css"])
    save_rendered_content(css_content, css_output_path)

    # Render and save api file
    if "api" in current_config:
        api_content = render_template(os.path.join(config_dir, current_config["api"]), context)
        api_name = name.replace(".html",".py")
        api_output_path = os.path.join(BUILD_DIR, path,"api" , api_name)
        save_rendered_content(api_content, api_output_path)

    # Render and save JavaScript file
    js_content = render_template(os.path.join(config_dir, current_config["javascript"]), context)
    js_output_path = os.path.join(BUILD_DIR, path, current_config["javascript"]) if path else \
                     os.path.join(BUILD_DIR, current_config["javascript"])
    save_rendered_content(js_content, js_output_path)

    # Copy HTML template file
    html_template_path = os.path.join(config_dir, current_config["template"])
    html_content = render_template(html_template_path, context)
    html_output_path = os.path.join(BUILD_DIR, path, 'template',\
                         f"{index}_{current_config['template']}")
    save_rendered_content(html_content,html_output_path)

    # Copy static files in Challenges/path/static
    if "static_files" in current_config:
        for static_file in current_config["static_files"]:
            source_file = os.path.join(config_dir, static_file)
            destination_file = os.path.join(BUILD_DIR, path, static_file)
            shutil.copy(source_file, destination_file)

def handle_last_challenge(config: Dict) -> None:
    """
    Handles the last challenge of a path.

    :param config: Dictionary containing the last challenge configuration.
    """
    None



def read_challenge_config(file_path: str) -> Dict:
    """
    Reads the challenge configuration from a YAML file.

    :param file_path: Path to the YAML configuration file.
    :return: Dictionary containing the configuration.
    """
    full_path = file_path

    with open(full_path, 'r',encoding='utf-8') as file:
        return yaml.safe_load(file)


def save_rendered_content(content: str, output_path: str) -> None:
    """
    Saves rendered content to a file.

    :param content: The rendered content to save.
    :param output_path: The file path to save the content to.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w',encoding='utf-8') as file:
        file.write(content)


def add_other_file_to_build(build_dir:str,paths_type:Dict)->None:
    """
    In order that the build is totally operational, api.py and other files must be included in build
    """

    api_file='./api.py'
    requirement_file='./requirements.txt'
    path_config_file='./paths_config.yml'
    main_file='./main.py'
    vercel_file='./vercel.json'
    templates_dir='./templates'
    static_dir='./static'

    shutil.copy(api_file, build_dir)
    shutil.copy(vercel_file, build_dir)
    shutil.copy(requirement_file, build_dir)
    shutil.copy(path_config_file, build_dir)
    shutil.copy(main_file, build_dir)

    shutil.copytree(templates_dir,os.path.join(build_dir,'templates'))
    shutil.copytree(static_dir,os.path.join(build_dir,'static'))

    # ajoute le favicon dans chaque dossier static pour qu'il soit accessible par les chalenges
    all_folder_path = list(paths_type)
    all_folder_path.append("initial")
    for path_type in all_folder_path:
        shutil.copy(os.path.join(static_dir,"favicon.ico"),\
                    os.path.join(build_dir,path_type,"static"))

    print("les fichiers API, MAIN, etc... et les dossiers de templates/static ont été copiés")

def prepare_static_files(build_dir: str, paths: Dict[str, list]) -> None:
    """
    Prepares static files for each challenge based on their configurations.
    Iterates over each path and challenge, reads the configuration, and generates the challenge.
    """
    # Clean the build directory first
    clean_build_directory(build_dir)
    # for each challenge in the initial path (everyones has the same initial path)
    #  build the challenge
    for index,challenges_init in enumerate(paths["INITIAL"]):
        config_path = challenges_init
        config_dir = os.path.dirname(config_path)
        print(config_dir)
        current_config = read_challenge_config(config_path)

        next_config: Optional[Dict] = None
        # if it has a next challenge load the cofiguration
        if index + 1 < len(paths["INITIAL"]):
            next_challenge_config_file = paths["INITIAL"][index + 1]
            next_config_path = next_challenge_config_file
            next_config = read_challenge_config(next_config_path)
        # whether it has a next challenge or not, create the challenge.
        generate_challenge(current_config, next_config, config_dir,index, "initial")

    # for each challenge in paths build the challenge
    for path_name, challenges in paths["PATHS"].items():
        for index, challenge_config_file in enumerate(challenges):
            config_path = challenge_config_file
            config_dir = os.path.dirname(config_path)
            print(config_dir)
            current_config = read_challenge_config(config_path)

            next_config: Optional[Dict] = None
            # if it has a next challenge load the cofiguration
            if index + 1 < len(challenges):
                next_challenge_config_file = challenges[index + 1]
                next_config_path = next_challenge_config_file
                next_config = read_challenge_config(next_config_path)
                # whether it has a next challenge or not, create the challenge.
            generate_challenge(current_config, next_config, config_dir, \
                               len(paths["INITIAL"])+index, path_name)
    # when everything is build add static files / api / etc to the build        
    add_other_file_to_build(build_dir,paths["PATHS"].keys())

if __name__ == "__main__":
    BUILD_DIR = "./build"
    # Read the paths configuration
    with open('paths_config.yml', 'r', encoding='utf-8') as file:
        PATHS = yaml.safe_load(file)
    prepare_static_files(BUILD_DIR, PATHS)
