import logging
from typing import Dict, Any, Optional

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest

from fastapi import APIRouter

from starlette.requests import Request
from starlette.responses import Response

from dispatch.database.core import engine, sessionmaker, SessionLocal
from dispatch.organization import service as organization_service
from dispatch.conversation import service as conversation_service
from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser

from .models import SubjectMetadata


app = AsyncApp(token="foo", raise_error_for_unhandled_request=True)
router = APIRouter()

logging.basicConfig(level=logging.DEBUG)


async def button_context_middleware(payload, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(payload["value"])})
    await next()


async def action_context_middleware(body, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(body["view"]["private_metadata"])})
    await next()


async def message_context_middleware(body, context, next):
    """Attemps to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(**body["message"]["metadata"]["event_payload"])})
    await next()


async def user_middleware(body, db_session, client, context, next):
    """Attempts to determine the user making the request."""
    email = (await client.users_info(user=body["user"]["id"]))["user"]["profile"]["email"]
    context["user"] = user_service.get_or_create(
        db_session=db_session,
        organization=context["subject"].organization_slug,
        user_in=DispatchUser(email=email),
    )
    await next()


async def modal_submit_middleware(body, context, next):
    """Parses view data into a reasonable data struct."""
    parsed_data = {}
    state_elem = body["view"].get("state")
    state_values = state_elem.get("values")

    for state in state_values:
        state_key_value_pair = state_values[state]

        for elem_key in state_key_value_pair:
            elem_key_value_pair = state_values[state][elem_key]

            if elem_key_value_pair.get("selected_option") and elem_key_value_pair.get(
                "selected_option"
            ).get("value"):
                parsed_data[state] = {
                    "name": elem_key_value_pair.get("selected_option").get("text").get("text"),
                    "value": elem_key_value_pair.get("selected_option").get("value"),
                }
            elif "selected_options" in elem_key_value_pair.keys():
                name = "No option selected"
                value = ""

                if elem_key_value_pair.get("selected_options"):
                    options = []
                    for selected in elem_key_value_pair["selected_options"]:
                        name = selected.get("text").get("text")
                        value = selected.get("value")
                        options.append({"name": name, "value": value})

                    parsed_data[state] = options
            elif elem_key_value_pair.get("selected_date"):
                parsed_data[state] = elem_key_value_pair.get("selected_date")
            else:
                parsed_data[state] = elem_key_value_pair.get("value")

    context["form_data"] = parsed_data
    next()


async def command_context_middleware(context, respond, next):
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
    else:
        respond(
            text="Unable to determine command context. Please ensure you are running command from an incident channel.",
            response_type="ephemeral",
        )
        return

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
    await next()


async def db_middleware(context, next):
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
    await next()


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
