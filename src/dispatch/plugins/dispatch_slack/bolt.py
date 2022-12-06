import logging
from typing import Dict, Any, Optional

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest
from slack_bolt.error import BoltUnhandledRequestError


from fastapi import APIRouter

from starlette.requests import Request
from starlette.responses import Response

app = AsyncApp(token="foo", raise_error_for_unhandled_request=True)
router = APIRouter()

logging.basicConfig(level=logging.DEBUG)


@app.error
async def errors(error, body, logger, respond):
    logger.exception(error)
    # if isinstance(error, BoltUnhandledRequestError):
    #    # you may want to have some logging here
    #    await respond("The command you have run is not current enabled.")
    #    return BoltResponse(status=200, body="")
    # else:
    #    # other error patterns
    #    await respond(str(error))
    #    return BoltResponse(status=200, body="")


async def to_bolt_request(
    req: Request,
    body: bytes,
    addition_context_properties: Optional[Dict[str, Any]] = None,
) -> BoltRequest:
    request = BoltRequest(
        body=body.decode("utf-8"),
        query=req.query_params,
        headers=req.headers,
    )
    if addition_context_properties is not None:
        for k, v in addition_context_properties.items():
            request.context[k] = v
    return await request


async def to_starlette_response(bolt_resp: BoltResponse) -> Response:
    resp = Response(
        status_code=bolt_resp.status,
        content=bolt_resp.body,
        headers=bolt_resp.first_headers_without_set_cookie(),
    )
    for cookie in bolt_resp.cookies():
        for name, c in cookie.items():
            resp.set_cookie(
                key=name,
                value=c.value,
                max_age=c.get("max-age"),
                expires=c.get("expires"),
                path=c.get("path"),
                domain=c.get("domain"),
                secure=True,
                httponly=True,
            )
    return await resp


class SlackRequestHandler:
    def __init__(self, app: AsyncApp):  # type: ignore
        self.app = app

    async def handle(
        self, req: Request, addition_context_properties: Optional[Dict[str, Any]] = None
    ) -> Response:
        body = await req.body()
        bolt_resp = self.app.dispatch(to_bolt_request(req, body, addition_context_properties))
        return to_starlette_response(bolt_resp)


handler = SlackRequestHandler(app)


@router.post(
    "/slack/event",
)
async def slack_events(request: Request):
    """Handle all incoming Slack events."""
    return await handler.handle(request)


@router.post(
    "/slack/command",
)
async def slack_commands(request: Request):
    """Handle all incoming Slack commands."""
    return await handler.handle(request)


@router.post(
    "/slack/action",
)
async def slack_actions(request: Request):
    """Handle all incoming Slack actions."""
    return await handler.handle(request)


@router.post(
    "/slack/menu",
)
async def slack_menus(request: Request):
    """Handle all incoming Slack actions."""
    return await handler.handle(request)
