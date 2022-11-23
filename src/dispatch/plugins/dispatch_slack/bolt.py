import logging
from typing import Optional
from pydantic import BaseModel

from slack_bolt.app import App
from slack_bolt.error import BoltUnhandledRequestError
from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest

from fastapi import BackgroundTasks

from dispatch.database.core import engine, sessionmaker, SessionLocal
from dispatch.organization import service as organization_service
from dispatch.conversation import service as conversation_service

from .actions import handle_slack_action
from .commands import handle_slack_command
from .events import handle_slack_event, EventEnvelope
from .menus import handle_slack_menu


app = App(raise_error_for_unhandled_request=True)

logging.basicConfig(level=logging.DEBUG)


class SubjectMetadata(BaseModel):
    id: Optional[str]
    type: Optional[str]
    organization_slug: str
    project_id: Optional[str]
    channel_id: Optional[str]


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
    error: Exception, body: BoltRequest, payload, client, logger
) -> Optional[BoltResponse]:
    if isinstance(error, BoltUnhandledRequestError):
        background_tasks = BackgroundTasks()

        if body.type == "events_api":
            response = handle_slack_event(
                config=config,
                client=client,
                event=EventEnvelope(**payload),
                background_tasks=background_tasks,
            )

        if body.type == "slash_commands":
            response = handle_slack_command(
                config=config, client=client, request=payload, background_tasks=background_tasks
            )

        if body.type == "interactive":
            if payload["type"] == "block_suggestion":
                response = handle_slack_menu(
                    config=config,
                    client=client,
                    request=payload,
                )

            else:
                response = handle_slack_action(
                    config=config, client=client, request=payload, background_tasks=background_tasks
                )
        logger.info("BoltUnhandledRequestError: %s", error, exc_info=True)
        return BoltResponse(status=200, body=response)

    logging.exception("Uncaught exception: %s", error)
    return None
