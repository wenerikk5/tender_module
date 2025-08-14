import logging
import json
import random

from aiohttp import web


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )


log = logging.getLogger(__name__)
routes = web.RouteTableDef()


errors = [
    {"code": 500, "message": "Internal Server Error"},
    {"code": 502, "message": "Bad Gateway"},
    {"code": 503, "message": "Service Unavailable"},
    {"code": 504, "message": "Gateway Timeout"},
]


def return_error_reply():
    error = random.choice(errors)
    log.info(f"Returning error: {error!r}")
    return web.Response(
        status=error["code"],
        text=error["message"],
        content_type="application/json",
    )


@routes.get("/procedures")
async def list_procedures(request: web.Request):
    if random.random() < 0.2:
        return return_error_reply()

    try:
        with open("procedures.json", "r") as f:
            data = json.load(f)
        return web.json_response(data)
    except FileNotFoundError:
        return web.Response(status=404, text="JSON file not found.")
    except json.JSONDecodeError:
        return web.Response(status=500, text="Error decoding JSON file.")


@routes.get("/procedures/details")
async def get_procedure_details(request: web.Request):
    if random.random() < 0.2:
        return return_error_reply()

    try:
        with open("lots.json", "r") as f:
            data = json.load(f)
        return web.json_response(data)
    except FileNotFoundError:
        return web.Response(status=404, text="JSON file not found.")
    except json.JSONDecodeError:
        return web.Response(status=500, text="Error decoding JSON file.")


app = web.Application()
app.add_routes(routes)


def main():
    configure_logging()
    web.run_app(app)


if __name__ == "__main__":
    main()
