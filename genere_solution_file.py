from typing import Optional, Dict
import yaml #pylint: disable=import-error

def read_challenge_config(file_path: str) -> Dict:
    """
    Reads the challenge configuration from a YAML file.

    :param file_path: Path to the YAML configuration file.
    :return: Dictionary containing the configuration.
    """
    full_path = file_path
    print(full_path)
    with open(full_path, 'r',encoding='UTF-8') as file:
        return yaml.safe_load(file)


def add_solution_to_file(suivant:str,path_name:str,index:int,current_config:Dict)-> None:
    """
    Add a solution to the solution file 
    """
    if suivant:
        solution=f"""
### Epreuve: `/{path_name.lower()}/{index}_{current_config["template"]}`
- **Next**: `/{path_name.lower()}/{suivant}`
- **Hint**: {current_config["hint"]}.
"""
    else:
        solution= f"""### Epreuve: `/{path_name.lower()}/{index}_{current_config["template"]}`
- **Hint**: {current_config["hint"]}.
"""
    with open('./solution.md','a') as file:
        file.write(f"{solution}\n")

def main(paths):
    for index in range(len(paths["INITIAL"])):
        chall_config=read_challenge_config(paths["INITIAL"][index])
        if index==0 and index+1<len(paths['INITIAL']):# premier challenge
            next=read_challenge_config(paths["INITIAL"][index+1])
            with open('./solution.md','a',encoding='UTF-8') as file:
                file.write(f"# Intro:\n\n## Epreuve `/`\n- **Next** : /{index+1}_{next['title']}\n- **Hint** : {chall_config['hint']}\n\n")
        elif index==0:
            file.write(f"# Intro:\n\n## Epreuve `/`\n- **Next** : Chosen Path\n- **Hint** : {chall_config['hint']}\n\n")
        elif index+1<len(paths['INITIAL']):
            next=read_challenge_config(paths['INITIAL'][index+1])
            with open('./solution.md','a',encoding='UTF-8') as file:
                file.write(f"## Epreuve `/{index}_{chall_config['title']}`\n- **Next** : /{index+1}_{next['title']}\n- **Hint** : {chall_config['hint']}\n\n")
        else:
             with open('./solution.md','a',encoding='UTF-8') as file:
                file.write(f"## Epreuve `/{index}_{chall_config['title']}`\n- **Next** : Chosen path - **Hint** : {chall_config['hint']}\n\n")


    for path_name, challenges in paths["PATHS"].items():
        with open('./solution.md','a',encoding='UTF-8') as file:
            file.write(f"## {path_name} Track `/{path_name.lower()}`:\n")
        for index, challenge_config_file in enumerate(challenges):
            config_path = challenge_config_file
            current_config = read_challenge_config(config_path)
            next_config: Optional[Dict] = None
            if index + 1 < len(challenges):
                next_challenge_config_file = challenges[index + 1]
                next_config_path = next_challenge_config_file
                next_config = read_challenge_config(next_config_path)
                next= f"{len(paths['INITIAL'])+index + 1}_{next_config['template']}" if next_config and "template" in next_config else None

            add_solution_to_file(next, path_name,len(paths["INITIAL"])+index,current_config)



if __name__=="__main__":
    with open('paths_config.yml', 'r',encoding='UTF-8') as file:
        PATHS = yaml.safe_load(file)
    main(PATHS)
