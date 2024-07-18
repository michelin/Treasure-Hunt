from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates



def create_router(templates: Jinja2Templates):
    router = APIRouter()
    @router.get("/{{chall_name}}")
    async def template(request: Request):
        data = {"request": request}
        var = templates.TemplateResponse("{{chall_name}}", data)
        return var

    @router.post("/{{chall_name}}")
    def send_flag():
        return {"message":"GG you finished the CTF Now create your own challs"} #"/{{sub_path}}/{{flag}} "}

    return router

router = create_router

