import yaml
import os
import glob
import importlib
import re

from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

with open('paths_config.yml', 'r') as file:
    data = yaml.safe_load(file)
    INITIAL= data["INITIAL"]
    PATHS = data["PATHS"]
BUILD_DIR = "."#"/build/"

app = FastAPI()
target_name="MICHELIN"
display_name="Michelin"

app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR,"initial","static")), name="static_initial")
app.mount("/static_common", StaticFiles(directory=os.path.join(BUILD_DIR,"static")), name="static")
base_templates = Jinja2Templates(directory=os.path.join(BUILD_DIR,"initial","template"))
error_template = Jinja2Templates(directory=os.path.join(BUILD_DIR,"templates"))



@app.get("/")
def read_root(request: Request):
    first_file = next((f for f in os.listdir(os.path.join(BUILD_DIR,"initial","template")) if re.search(r"0_", f)), None)
    donnees = {"request": request, "target_name":target_name, "display_name": display_name}
    return base_templates.TemplateResponse(first_file, donnees)

def find_router_modules(directory):
    """Trouver tous les fichiers Python dans le dossier spécifié."""
    module_paths = glob.glob(os.path.join(directory, "*.py"))
    return [os.path.splitext(os.path.basename(path))[0] for path in module_paths]

def load_routers(directory, module_names):
    """Charger dynamiquement les routeurs à partir des noms de modules."""
    routers = []
    for module_name in module_names:
        module = importlib.import_module(f"{directory}.{module_name}")
        if hasattr(module, "router"):
            routers.append(module.router)
    return routers

# Create a router and a Jinja2Templates instance for each path
routers = {}
key_list=list(PATHS.keys())
key_list.append("initial")
for path in key_list:
    # Create the directory path for the templates
    template_dir = os.path.join(BUILD_DIR, path, "template")

    # Create the directory path for the static files
    static_dir = os.path.join(BUILD_DIR, path, "static")

    # Create an APIRouter instance
    router = APIRouter()
    # Mount static files to the router
    router.mount("/static", StaticFiles(directory=static_dir), name="static_" + path)

    router_directory = os.path.join(BUILD_DIR, path, "api")
    router_modules = find_router_modules(router_directory)
    api_routers = load_routers(f"{ path }.api", router_modules)

    # Create a Jinja2Templates instance
    templates = Jinja2Templates(directory=template_dir)

    for new_router in api_routers:
        router.include_router(new_router(templates))


    # Add the router with templates and static files to the routers dictionary
    routers[path] = {
        "router": router,
        "templates": templates
    }

def create_challenge_route(templates: Jinja2Templates):
    async def challenge(request: Request, challenge: str):
        try:
            data = {"request": request}
            return templates.TemplateResponse(challenge, data)
        except Exception as e:
            print(e)
            return not_found_exception_handler(request,e)
    return challenge

# Add routes to each router
for path, elements in routers.items():
    router = elements["router"]
    templates = elements["templates"]


    challenge_route = create_challenge_route(templates)
    router.get("/{challenge}")(challenge_route)
    router.post("/{challenge}")(challenge_route)
    router.put("/{challenge}")(challenge_route)

    # Include the router in the main application with a path prefix
    if path=="initial":
        app.mount("/",router)
    else:
        app.mount(f"/{path}",router)


@app.get("/{challenge}")
def read_root_chall(request: Request, challenge: str):
    try:
        return base_templates.TemplateResponse(challenge, {"request": request})
    except Exception as e:
        print(e)
        return not_found_exception_handler(request,e)





async def get_body(request: Request):
    return await request.body()



@app.get("/hello/{name}")
def hello_name(name: str):
    return f"Hello {name}"




@app.exception_handler(404)
def not_found_exception_handler(request: Request, exc: HTTPException):
    print("error 404")
    return error_template.TemplateResponse('404.html', {'request': request})

