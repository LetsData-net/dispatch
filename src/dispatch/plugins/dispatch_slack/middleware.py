from dispatch.database.core import engine, sessionmaker, SessionLocal
from dispatch.organization import service as organization_service
from dispatch.conversation import service as conversation_service
from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser

from .models import SubjectMetadata


async def shortcut_context_middleware(body, context, next):
    """Attempts to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(channel_id=context["channel_id"])})
    await next()


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
    await next()


# TODO determine how we an get the current slack config
async def configuration_context_middleware(context, db_session, next):
    context["config"] = ""
    await next()


async def command_context_middleware(context, next):
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
            context.update(
                {
                    "subject": SubjectMetadata(
                        type="incident",
                        id=conversation.incident.id,
                        organization_slug=conversation.incident.project.organization.slug,
                        project_id=conversation.incident.project.id,
                    )
                }
            )
            scoped_db_session.close()
            break
    else:
        raise Exception(
            "Unable to determine command context. Please ensure you are running command from an incident channel."
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
