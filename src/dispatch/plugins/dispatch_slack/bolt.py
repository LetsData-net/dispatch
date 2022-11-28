import logging
import asyncio
from typing import Dict, Any, Optional

from slack_bolt.app import App
from slack_bolt.error import BoltUnhandledRequestError
from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest

from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import true

from starlette.requests import Request
from starlette.responses import Response

from dispatch.database.core import engine, sessionmaker, SessionLocal
from dispatch.organization import service as organization_service
from dispatch.conversation import service as conversation_service
from dispatch.plugin.models import PluginInstance, Plugin

from .actions import handle_slack_action
from .commands import handle_slack_command
from .events import handle_slack_event, EventEnvelope
from .menus import handle_slack_menu
from .actions import handle_block_action, handle_dialog_action, handle_modal_action
from .models import SubjectMetadata


app = App(raise_error_for_unhandled_request=True)
router = APIRouter()

logging.basicConfig(level=logging.DEBUG)


def button_context_middleware(payload, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(payload["value"])})
    next()


def action_context_middleware(body, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(body["view"]["private_metadata"])})
    next()


def message_context_middleware(body, context, next):
    """Attemps to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(**body["message"]["metadata"]["event_payload"])})
    next()


def slash_command_context_middleware(context, next):
    db_session = SessionLocal()
    organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]
    db_session.close()

    conversation = None
    for slug in organization_slugs:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        scoped_db_session = sessionmaker(bind=schema_engine)()
        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=scoped_db_session, channel_id=context["channel_id"]
        )
        if conversation:
            scoped_db_session.close()
            break

    context.update(
        {
            "subject": SubjectMetadata(
                type="incident",
                id=conversation.incident.id,
                organization_slug=conversation.project.organization.slug,
                project_id=conversation.project.id,
            )
        }
    )
    next()


def db_middleware(context, next):
    if not context.get("subject"):
        db_session = SessionLocal()
        slug = organization_service.get_default(db_session=db_session).slug
        context.update({"subject": SubjectMetadata(organization_slug=slug)})
        db_session.close()
    else:
        slug = context["subject"].organization_slug

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{slug}",
        }
    )
    context["db_session"] = sessionmaker(bind=schema_engine)()
    next()


@app.error
def custom_error_handler(
    error: Exception, body: BoltRequest, payload, client, context, logger
) -> Optional[BoltResponse]:

    # this will handle all legacy slack interactions until they can be moved to bolt
    if isinstance(error, BoltUnhandledRequestError):
        background_tasks = BackgroundTasks()

        # There is currently no reasonable way to extract which organization a request refers to.
        # With the transistion to Bolt organization will be encoded in every message.
        db_session = SessionLocal()
        slug = organization_service.get_default(db_session=db_session).slug
        db_session.close()

        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )
        db_session = sessionmaker(bind=schema_engine)()
        plugin = (
            db_session.query(PluginInstance)
            .join(Plugin)
            .filter(PluginInstance.enabled == true(), Plugin.slug == "slack-conversation")
            .first()
        )
        config = plugin.instance.configuration

        if body.get("command"):
            response = handle_slack_command(
                config=config, client=client, request=payload, background_tasks=background_tasks
            )
        else:
            if body["type"] == "events_api":
                response = handle_slack_event(
                    config=config,
                    client=client,
                    event=EventEnvelope(**payload),
                    background_tasks=background_tasks,
                )

            if body["type"] == "interactive":
                if payload["type"] == "block_suggestion":
                    response = handle_slack_menu(
                        config=config,
                        client=client,
                        request=payload,
                    )

                else:
                    response = handle_slack_action(
                        config=config,
                        client=client,
                        request=payload,
                        background_tasks=background_tasks,
                    )

            if body["type"] == "view_submission":
                response = handle_modal_action(config, body, background_tasks)

            if body["type"] == "dialog_submission":
                response = handle_dialog_action(config, body, background_tasks)

            if body["type"] == "block_actions":
                response = handle_block_action(config, body, background_tasks)

        # this is needed because all of our current functions are async
        response = asyncio.run(response)
        logger.info("BoltUnhandledRequestError: %s", error, exc_info=True)
        return BoltResponse(status=200, body=response)

    logging.exception("Uncaught exception: %s", error)
    return None


def to_bolt_request(
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
    return request


def to_starlette_response(bolt_resp: BoltResponse) -> Response:
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
    return resp


class SlackRequestHandler:
    def __init__(self, app: App):  # type: ignore
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
