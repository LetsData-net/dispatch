from datetime import datetime
from typing import List

import pytz
from blockkit import (
    Actions,
    Button,
    Checkboxes,
    Context,
    Divider,
    Image,
    Input,
    MarkdownText,
    Modal,
    PlainOption,
    PlainTextInput,
    Section,
    UsersSelect,
)
from sqlalchemy import func

from dispatch.database.core import resolve_attr
from dispatch.document import service as document_service
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.individual import service as individual_service
from dispatch.monitor import service as monitor_service
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    command_context_middleware,
    db_middleware,
    message_context_middleware,
    modal_submit_middleware,
    user_middleware,
)
from dispatch.plugins.dispatch_slack.fields import (
    DefaultBlockIds,
    datetime_picker_block,
    description_input,
    incident_priority_select,
    incident_severity_select,
    incident_type_select,
    participant_select,
    project_select,
    resolution_input,
    static_select_block,
    title_input,
    tag_multi_select,
)
from dispatch.plugins.dispatch_slack.incident.enums import (
    AddTimelineEventActions,
    AddTimelineEventBlockIds,
    AssignRoleActions,
    AssignRoleBlockIds,
    EngageOncallActions,
    EngageOncallBlockIds,
    IncidentReportActions,
    IncidentReportBlockIds,
    IncidentReportActionIds,
    IncidentUpdateActions,
    IncidentUpdateActionIds,
    IncidentUpdateBlockIds,
    LinkMonitorActionIds,
    LinkMonitorBlockIds,
    ReportExecutiveActions,
    ReportExecutiveBlockIds,
    ReportTacticalActions,
    ReportTacticalBlockIds,
    TaskNotificationActionIds,
    UpdateNotificationGroupActionIds,
    UpdateNotificationGroupActions,
    UpdateNotificationGroupBlockIds,
    UpdateParticipantActions,
)
from dispatch.plugins.dispatch_slack.models import SubjectMetadata
from dispatch.plugins.dispatch_slack.service import get_user_email, get_user_profile_by_email
from dispatch.project import service as project_service
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag
from dispatch.task import service as task_service
from dispatch.task.enums import TaskStatus
from dispatch.task.models import Task


class TaskMetadata(SubjectMetadata):
    resource_id: str


class MonitorMetadata(SubjectMetadata):
    weblink: str


def configure(config):
    """Maps commands/events to their functions."""
    middleware = [command_context_middleware, db_middleware]
    app.command(config.slack_command_add_timeline_event, middleware=middleware)(
        handle_add_timeline_event_command
    )
    app.command(config.slack_command_list_tasks, middleware=middleware)(handle_list_tasks_command)
    app.command(config.slack_command_list_my_tasks, middleware=middleware)(
        handle_list_tasks_command
    )
    app.command(config.slack_command_list_participants, middleware=middleware)(
        handle_list_participants_command
    )
    app.command(config.slack_command_assign_role, middleware=middleware)(handle_assign_role_command)
    app.command(config.slack_command_update_incident, middleware=middleware)(
        handle_update_incident_command
    )
    app.command(config.slack_command_update_participant, middleware=middleware)(
        handle_update_participant_command
    )
    app.command(config.slack_command_report_tactical, middleware=middleware)(
        handle_report_tactical_command
    )
    app.command(config.slack_command_report_executive, middleware=middleware)(
        handle_report_executive_command
    )
    app.command(config.slack_command_add_timeline_event, middleware=middleware)(
        handle_add_timeline_event_command
    )
    app.command(config.slack_command_list_incidents, middleware=middleware)(
        handle_list_incidents_command
    )
    app.command(config.slack_command_report_incident, middleware=middleware)(
        handle_report_incident_command
    )
    app.command(config.slack_command_update_incident, middleware=middleware)(
        handle_update_incident_command
    )

    app.event(config.timeline_event_reaction, middleware=[db_middleware])(
        handle_timeline_added_event
    )


async def handle_add_timeline_event_command(ack, body, respond, client, context, db_session):
    """Handles the add timeline event command."""
    ack()
    blocks = [
        Context(
            elements=[MarkdownText(text="Use this form to add an event to the incident timeline.")]
        ),
        datetime_picker_block(),
        description_input(),
    ]

    modal = Modal(
        title="Add Timeline Event",
        blocks=blocks,
        submit="Add",
        close="Close",
        callback_id=AddTimelineEventActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


@app.action(
    AddTimelineEventActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_add_timeline_submission_event(
    ack, body, respond, user, client, context, db_session, form_data
):
    """Handles the add timeline submission event."""
    ack()
    event_date = form_data.get(AddTimelineEventBlockIds.date)
    event_hour = form_data.get(AddTimelineEventBlockIds.hour)["value"]
    event_minute = form_data.get(AddTimelineEventBlockIds.minute)["value"]
    event_timezone_selection = form_data.get(AddTimelineEventBlockIds.timezone)["value"]
    event_description = form_data.get(AddTimelineEventBlockIds.description)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )

    event_timezone = event_timezone_selection
    if event_timezone_selection == "profile":
        participant_profile = get_user_profile_by_email(client, user.email)
        if participant_profile.get("tz"):
            event_timezone = participant_profile.get("tz")

    event_dt = datetime.fromisoformat(f"{event_date}T{event_hour}:{event_minute}")
    event_dt_utc = pytz.timezone(event_timezone).localize(event_dt).astimezone(pytz.utc)

    event_service.log_incident_event(
        db_session=db_session,
        source="Slack Plugin - Conversation Management",
        started_at=event_dt_utc,
        description=f'"{event_description}," said {participant.individual.name}',
        incident_id=context["subject"].id,
        individual_id=participant.individual.id,
    )

    respond("Event succesfully added to timeline.", response_type="ephemeral")


async def handle_list_incidents_command(ack, body, respond, db_session, context):
    """Handles the list incidents command."""
    ack()
    projects = []

    if context["subject"].type == "incident":
        # command was run in an incident conversation
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        projects.append(incident.project)
    else:
        # command was run in a non-incident conversation
        args = body["command"]["text"].split(" ")

        if len(args) == 2:
            project = project_service.get_by_name(db_session=db_session, name=args[1])

            if project:
                projects.append(project)
            else:
                respond(
                    text=f"Project name '{args[1]}' in organization '{args[0]}' not found. Check your spelling.",
                    response_type="ephemeral",
                )
                return
        else:
            projects = project_service.get_all(db_session=db_session)

    incidents = []
    for project in projects:
        # we fetch active incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session, project_id=project.id, status=IncidentStatus.active
            )
        )
        # We fetch stable incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.stable,
            )
        )
        # We fetch closed incidents in the last 24 hours
        incidents.extend(
            incident_service.get_all_last_x_hours_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.closed,
                hours=24,
            )
        )

    blocks = [Context(text="Incident List")]

    if incidents:
        for incident in incidents:
            if incident.visibility == Visibility.open:
                blocks.append(
                    Section(
                        fields=[
                            f"*<{incident.ticket.weblink}|{incident.name}>*",
                            f"*Title*:\n {incident.title}",
                            f"*Type*:\n {incident.incident_type.name}",
                            f"*Severity*:\n {incident.incident_severity.name}",
                            f"*Priority*:\n {incident.incident_priority.name}",
                            f"*Status*:\n{incident.status}",
                            f"*Incident Commander*:\n<{incident.commander.individual.weblink}|{incident.commander.individual.name}>",
                            f"*Project*:\n{incident.project.name}",
                        ]
                    )
                )

    respond(text="Incident List", blocks=blocks, response_type="ephemeral")


async def handle_list_participants_command(ack, body, respond, client, db_session, context):
    """Handles list participants command."""
    blocks = [Section(text="*Incident Participants*")]
    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=context["subject"].id
    ).all()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    contact_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="contact"
    )

    for participant in participants:
        if participant.active_roles:
            participant_email = participant.individual.email
            participant_info = contact_plugin.instance.get(participant_email, db_session=db_session)
            participant_name = participant_info.get("fullname", participant.individual.email)
            participant_team = participant_info.get("team", "Unknown")
            participant_department = participant_info.get("department", "Unknown")
            participant_location = participant_info.get("location", "Unknown")
            participant_weblink = participant_info.get("weblink")

            participant_reason_added = participant.added_reason or "Unknown"
            if participant.added_by:
                participant_added_by = participant.added_by.individual.name
            else:
                participant_added_by = "Unknown"

            participant_active_roles = participant_role_service.get_all_active_roles(
                db_session=db_session, participant_id=participant.id
            )
            participant_roles = []
            for role in participant_active_roles:
                participant_roles.append(role.role)

            accessory = None
            # don't load avatars for large incidents
            if len(participants) < 20:
                participant_avatar_url = dispatch_slack_service.get_user_avatar_url(
                    client, participant_email
                )
                accessory = Image(image_url=participant_avatar_url, alt_text=participant_name)

            blocks.append(
                Section(
                    fields=[
                        f"*Name* \n<{participant_weblink}|{participant_name} ({participant_email})>",
                        f"*Team*\n {participant_team}, {participant_department}",
                        f"*Location* \n{participant_location}",
                        f"*Incident Role(s)* \n{(', ').join(participant_roles)}",
                        f"*Reason Added* \n{participant_reason_added}",
                        f"*Added By* \n{participant_added_by}",
                    ],
                    accessory=accessory,
                ),
                Divider(),
            )

    respond(text="Incident Participant List", blocks=blocks, response_type="ephemeral")


def filter_tasks_by_assignee_and_creator(tasks: List[Task], by_assignee: str, by_creator: str):
    """Filters a list of tasks looking for a given creator or assignee."""
    filtered_tasks = []
    for t in tasks:
        if by_creator:
            creator_email = t.creator.individual.email
            if creator_email == by_creator:
                filtered_tasks.append(t)
                # lets avoid duplication if creator is also assignee
                continue

        if by_assignee:
            assignee_emails = [a.individual.email for a in t.assignees]
            if by_assignee in assignee_emails:
                filtered_tasks.append(t)

    return filtered_tasks


async def handle_list_tasks_command(ack, user, body, respond, context, db_session):
    """Handles the list tasks command."""
    ack()
    blocks = []

    caller_only = False
    if body["command"] == SlackConversationConfiguration.slack_command_list_my_tasks:
        caller_only = True

    for status in TaskStatus:
        blocks.append(Section(text=f"*{status} Incident Tasks*"))
        button_text = "Resolve" if status == TaskStatus.open else "Re-open"

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=context["subject"].id, status=status
        )

        if caller_only:
            tasks = filter_tasks_by_assignee_and_creator(tasks, user.email, user.email)

        for idx, task in enumerate(tasks):
            assignees = [f"<{a.individual.weblink}|{a.individual.name}>" for a in task.assignees]

            button_metadata = TaskMetadata(
                type="incident",
                organization_slug=task.project.organization.slug,
                id=task.incident.id,
                project_id=task.project.id,
                resource_id=task.resource_id,
                channel_id=context["channel_id"],
            ).json()

            blocks.append(
                Section(
                    fields=[
                        f"*Description:* \n <{task.weblink}|{task.description}>",
                        f"*Creator:* \n <{task.creator.individual.weblink}|{task.creator.individual.name}>",
                        f"*Assignees:* \n {', '.join(assignees)}",
                    ],
                    accessory=Button(
                        text=button_text,
                        value=button_metadata,
                        action_id=TaskNotificationActionIds.update_status,
                    ),
                )
            )
            blocks.append(Divider())

    respond(text="Incident Task List", blocks=blocks, response_type="ephermeral")


async def handle_list_resources_command(ack, body, respond, client, db_session, context, logger):
    """Handles the list resources command."""
    ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    incident_description = (
        incident.description
        if len(incident.description) <= 500
        else f"{incident.description[:500]}..."
    )

    blocks = [
        Section(text=f"*<{incident.title}>*"),
        Section(text=incident_description),
        Section(text=incident.commander.individual.name),
    ]

    # optional blocks
    for i in [
        "incident_document.weblink",
        "storage_weblink",
        "ticket.weblink",
        "conference.weblink",
        "conference.conference_challenge",
        "incident_review_document",
    ]:
        attr = resolve_attr(incident, i)
        if attr:
            blocks.append(Section(text=f"*<{attr}>*"))

    message_kwargs = {
        "title": incident.title,
        "description": incident_description,
        "commander_fullname": incident.commander.individual.name,
        "commander_team": incident.commander.team,
        "commander_weblink": incident.commander.individual.weblink,
        "reporter_fullname": incident.reporter.individual.name,
        "reporter_team": incident.reporter.team,
        "reporter_weblink": incident.reporter.individual.weblink,
    }

    faq_doc = document_service.get_incident_faq_document(
        db_session=db_session, project_id=incident.project_id
    )
    if faq_doc:
        blocks.append(Section(text=f"*<{faq_doc.weblink}|FAQ Document>*"))

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session, project_id=incident.project_id
    )
    if conversation_reference:
        blocks.append(Section(text=f"*<{conversation_reference.weblink}|Command Reference>*"))

        message_kwargs.update(
            {"conversation_commands_reference_document_weblink": conversation_reference.weblink}
        )

    respond(text="Incident Resources Message", blocks=blocks, response_type="ephemeral")


async def handle_timeline_added_event(ack, body, client, context, db_session):
    """Handles an event where a reaction is added to a message."""
    conversation_id = context["channel_id"]
    message_ts = context["ts"]
    message_ts_utc = datetime.datetime.utcfromtimestamp(float(message_ts))

    # we fetch the message information
    response = dispatch_slack_service.list_conversation_messages(
        client, conversation_id, latest=message_ts, limit=1, inclusive=1
    )
    message_text = response["messages"][0]["text"]
    message_sender_id = response["messages"][0]["user"]

    # TODO handle case reactions
    if context["subject"].type == "incident":
        # we fetch the incident
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

        # we fetch the individual who sent the message
        message_sender_email = get_user_email(client=client, user_id=message_sender_id)
        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=message_sender_email, project_id=incident.project.id
        )

        # we log the event
        event_service.log_incident_event(
            db_session=db_session,
            source="Slack Plugin - Conversation Management",
            description=f'"{message_text}," said {individual.name}',
            incident_id=context["subject"].id,
            individual_id=individual.id,
            started_at=message_ts_utc,
        )


@app.message(
    {"type": "message"}, middleware=[message_context_middleware, user_middleware, db_middleware]
)
async def handle_participant_role_activity(ack, db_session, context, user):
    """Increments the participant role's activity counter."""
    ack()

    # TODO add when case support when participants are added.
    if context["subject"].type == "incident":
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )

        if participant:
            active_participant_roles = participant.active_roles
            for participant_role in active_participant_roles:
                participant_role.activity += 1

            # re-assign role once threshold is reached
            if participant_role.role == ParticipantRoleType.observer:
                if participant_role.activity >= 10:  # ten messages sent to the incident channel
                    # we change the participant's role to the participant one
                    participant_role_service.renounce_role(
                        db_session=db_session, participant_role=participant_role
                    )
                    participant_role_service.add_role(
                        db_session=db_session,
                        participant_id=participant.id,
                        participant_role=ParticipantRoleType.participant,
                    )

                    # we log the event
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Slack Plugin - Conversation Management",
                        description=(
                            f"{participant.individual.name}'s role changed from {participant_role.role} to "
                            f"{ParticipantRoleType.participant} due to activity in the incident channel"
                        ),
                        incident_id=context["subject"].id,
                    )


@app.message(
    {"type": "message"}, middleware=[message_context_middleware, user_middleware, db_middleware]
)
async def handle_after_hours_message(ack, context, body, client, respond, user, db_session):
    """Notifies the user that this incident is current in after hours mode."""
    # we ignore user channel and group join messages
    ack()

    if body["subtype"] in ["channel_join", "group_join"]:
        return

    if context["subject"].type == "case":
        return

    # get their timezone from slack
    elif context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        owner_email = incident.commander.individual.email
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )

        # get their timezone from slack
        owner_tz = dispatch_slack_service.get_user_info_by_email(client, email=owner_email)["tz"]

        message = f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}* and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {owner_tz} timezone)."

    now = datetime.datetime.now(pytz.timezone(owner_tz))
    is_business_hours = now.weekday() not in [5, 6] and 9 <= now.hour < 17

    if not is_business_hours:
        if not participant.after_hours_notification:
            blocks = [Section(text=message)]
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()
            respond(blocks=blocks, response_type="ephemeral")


@app.event("member_joined", middleware=[action_context_middleware, user_middleware, db_middleware])
async def handle_member_joined_channel(ack, user, body, client, db_session, context):
    """Handles the member_joined_channel Slack event."""
    ack()
    participant = incident_flows.incident_add_or_reactivate_participant_flow(
        user_email=user.email, incident_id=context["subject"].id, db_session=db_session
    )

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    if body["inviter"]:
        inviter_email = get_user_email(client=client, user_id=body["inviter"])
        client.user
        added_by_participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=inviter_email
        )
        participant.added_by = added_by_participant
        participant.added_reason = body["text"]
    else:
        participant.added_by = incident.commander
        participant.added_reason = f"Participant added by {added_by_participant.individual.name}"

    db_session.add(participant)
    db_session.commit()


@app.event("member_left", middleware=[action_context_middleware, db_middleware])
async def handle_member_left_channel(ack, context, db_session, user):
    ack()
    incident_flows.incident_remove_participant_flow(
        user.email, context["subject"].id, db_session=db_session
    )


@app.event(
    {"type": "message", "subtype": "message_replied"}, middleware=[action_context_middleware]
)
async def handle_thread_creation(ack, respond, client, context):
    """Sends the user an ephemeral message if they use threads."""
    if not SlackConversationConfiguration.ban_threads:
        return

    message = "Please refrain from using threads in incident related channels. Threads make it harder for incident participants to maintain context."
    respond(text=message, response_type="ephemeral")


@app.message({"type": "message"}, middleware=[message_context_middleware, db_middleware])
async def handle_message_tagging(ack, db_session, context):
    """Looks for incident tags in incident messages."""

    # TODO handle case tagging
    if context["subject"].type == "incident":
        text = context["text"]
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        tags = tag_service.get_all(db_session=db_session, project_id=incident.project.id).all()
        tag_strings = [t.name.lower() for t in tags if t.discoverable]
        phrases = build_term_vocab(tag_strings)
        matcher = build_phrase_matcher("dispatch-tag", phrases)
        extracted_tags = list(set(extract_terms_from_text(text, matcher)))

        matched_tags = (
            db_session.query(Tag)
            .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
            .all()
        )

        incident.tags.extend(matched_tags)
        db_session.commit()


@app.message({"type": "message"}, middleware=[message_context_middleware, db_middleware])
async def handle_message_monitor(ack, respond, body, context, db_session):
    """Looks strings that are available for monitoring (usually links)."""
    ack()
    # TODO handle cases
    if context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        project_id = incident.project.id
        button_metadata = MonitorMetadata(
            type="incident",
            organization_slug=incident.project.organization.slug,
            id=incident.id,
            project_id=incident.project.id,
            channel_id=context["channel_id"],
        )

    else:
        return

    plugins = plugin_service.get_active_instances(
        db_session=db_session, project_id=project_id, plugin_type="monitor"
    )

    for p in plugins:
        for matcher in p.instance.get_matchers():
            for match in matcher.finditer(body["text"]):
                match_data = match.groupdict()
                monitor = monitor_service.get_by_weblink(
                    db_session=db_session, weblink=match_data["weblink"]
                )

                # silence ignored matches
                if monitor:
                    continue

                current_status = p.instance.get_match_status(match_data)
                if current_status:
                    status_text = ""
                    for k, v in current_status.items():
                        status_text += f"*{k.title()}*:\n{v.title()}\n"

                    button_metadata.weblink = match_data["weblink"]

                    blocks = [
                        Section(
                            text="Hi! Dispatch is able to help track the status of: \n {match_data['weblink']} \n\n Would you like for changes in it's status to be propagated to this incident channel?"
                        ),
                        Section(text=status_text),
                        Actions(
                            block_id=LinkMonitorBlockIds.monitor,
                            elements=[
                                Button(
                                    text="Monitor",
                                    action_id=LinkMonitorActionIds.monitor,
                                    style="primary",
                                    value=button_metadata,
                                ),
                                Button(
                                    text="Ignore",
                                    action_id=LinkMonitorActionIds.ignore,
                                    style="primary",
                                    value=button_metadata,
                                ),
                            ],
                        ),
                    ]
                    respond(blocks=blocks, response_type="ephemeral")


async def handle_update_participant_command(ack, respond, body, context, db_session, client):
    """Handles the update participant command."""
    ack()
    if context["subject"].type == "case":
        respond(text="This command is not yet supported in the case context.")

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    participants = [p.name for p in incident.participants]

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Use this form to update the reason why the participant was added to the incident."
                )
            ]
        ),
        Input(
            PlainTextInput(placeholder="Reason for addition"),
            label="Reason added",
            block_id=UpdateNotificationGroupBlockIds.reason,
        ),
        participant_select(
            block_id=UpdateNotificationGroupBlockIds.participant,
            participants=participants,
        ),
    ]

    modal = Modal(
        title="Update Participant",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=UpdateParticipantActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.view_open(trigger_id=body["trigger_id"], view=modal)


async def handle_update_notifications_group_command(ack, body, context, client, db_session):
    """Handles the update notification group command."""
    ack()

    # TODO handle cases
    if context["subject"].type == "case":
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    members = group_plugin.instance.list(incident.notifications_group.email)

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Use this form to update the membership of the notifications group."
                )
            ]
        ),
        Input(
            label="Members",
            element=PlainTextInput(
                text=", ".join(members),
                multiline=True,
                action_id=UpdateNotificationGroupActionIds.members,
            ),
            block_id=UpdateNotificationGroupBlockIds.members,
        ),
        Context(elements=MarkdownText(text="Separate email addresses with commas")),
    ]

    modal = Modal(
        title="Update Group Membership",
        blocks=blocks,
        close="Cancel",
        submit="Submit",
        callback_id=UpdateNotificationGroupActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def handle_assign_role_command(ack, context, body, client):
    """Handles the assign role command."""
    ack()

    roles = [r for r in ParticipantRoleType if r != ParticipantRoleType.participant]

    blocks = [
        Context(
            elements=[
                PlainTextInput(
                    text="Assign a role to a participant. Note: User will be invited to incident channel if they are not yet a member."
                )
            ]
        ),
        Section(text="Select User", block_id=AssignRoleBlockIds.user, accessory=UsersSelect()),
        static_select_block(
            placeholder="Select Role", options=roles, block_id=AssignRoleBlockIds.role
        ),
    ]

    modal = Modal(
        title="Assign Role",
        submit="Assign",
        close="Cancel",
        blocks=blocks,
        callback_id=AssignRoleActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def handle_engage_oncall_command(ack, respond, context, body, client, db_session):
    """Handles the engage oncall command."""
    ack()
    # TODO handle cases
    if context["subject"].type == "case":
        respond(text="Command is not currently available for cases.", response_type="ephemeral")
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    oncall_services = service_service.get_all_by_project_id_and_status(
        db_session=db_session, project_id=incident.project.id, is_active=True
    )

    if not oncall_services.count():
        respond(
            blocks=[
                Section(
                    text="No oncall services have been defined. You can define them in the Dispatch UI at /services."
                )
            ],
            response_type="ephemeral",
        )
        return

    services = [s.name for s in oncall_services]

    blocks = [
        static_select_block(
            label="Service",
            block_id=EngageOncallBlockIds.service,
            placeholder="Select Service",
            options=services,
        ),
        Checkboxes(options=[PlainOption(text="Page")], block_id=EngageOncallBlockIds.page),
    ]

    modal = Modal(
        title="Engage Oncall",
        blocks=blocks,
        submit="Engage",
        close="Close",
        callback_id=EngageOncallActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def handle_report_tactical_command(ack, client, respond, context, db_session, body):
    """Handles the report tactical command."""
    ack()

    if context["subject"].type == "case":
        respond(
            text="Command is not available outside of incident channels.", response_type="ephemeral"
        )
        return

    # we load the most recent tactical report
    tactical_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session,
        incident_id=context["subject"].id,
        report_type=ReportTypes.tactical_report,
    )

    conditions = actions = needs = None
    if tactical_report:
        conditions = tactical_report.details.get("conditions")
        actions = tactical_report.details.get("actions")
        needs = tactical_report.details.get("needs")

    blocks = [
        Input(
            label="Conditions",
            element=PlainTextInput(
                placeholder="Current incident conditions", initial_value=conditions, multiline=True
            ),
            block_id=ReportTacticalBlockIds.conditions,
        ),
        Input(
            label="Actions",
            element=PlainTextInput(
                placeholder="Current incident actions", initial_value=actions, multiline=True
            ),
            block_id=ReportTacticalBlockIds.actions,
        ),
        Input(
            label="Needs",
            element=PlainTextInput(
                placeholder="Current incident needs", initial_value=needs, multiline=True
            ),
            block_id=ReportTacticalBlockIds.needs,
        ),
    ]

    modal = Modal(
        title="Tactical Report",
        blocks=blocks,
        submit="Submit",
        close="Close",
        callback_id=ReportTacticalActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def handle_report_executive_command(ack, body, client, respond, context, db_session):
    """Handles executive report command."""
    ack()

    if context["subject"].type == "case":
        respond(
            text="Command is not available outside of incident channels.", response_type="ephemeral"
        )
        return

    executive_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session,
        incident_id=context["subject"].id,
        report_type=ReportTypes.executive_report,
    )

    current_status = overview = next_steps = None
    if executive_report:
        current_status = executive_report.details.get("current_status")
        overview = executive_report.details.get("overview")
        next_steps = executive_report.details.get("next_steps")

    blocks = [
        Input(
            label="Current Status",
            element=PlainTextInput(
                placeholder="Current incident status", initial_value=current_status, multiline=True
            ),
            block_id=ReportExecutiveBlockIds.current_status,
        ),
        Input(
            label="Overview",
            element=PlainTextInput(placeholder="Overview", initial_value=overview, multiline=True),
            block_id=ReportExecutiveBlockIds.overview,
        ),
        Input(
            label="Next Steps",
            element=PlainTextInput(
                placeholder="Current incident needs", initial_value=next_steps, multiline=True
            ),
            block_id=ReportExecutiveBlockIds.next_steps,
        ),
        Context(
            elements=[
                MarkdownText(
                    text=f"Use {SlackConversationConfiguration.slack_command_update_notifications_group} to update the list of recipients of this report."
                )
            ]
        ),
    ]

    modal = Modal(
        title="Executive Report",
        blocks=blocks,
        submit="Submit",
        close="Close",
        callback_id=ReportExecutiveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def handle_update_incident_command(ack, body, client, context, db_session):
    """Creates the incident update modal."""
    ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update incident details.")]),
        title_input(initial_value=incident.title),
        description_input(initial_value=incident.description),
        resolution_input(initial_value=incident.resolution),
        project_select(
            db_session=db_session,
            initial_option=incident.project.name,
            action_id=IncidentUpdateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option=incident.incident_type.name,
            project_id=incident.project.id,
        ),
        incident_priority_select(
            db_session=db_session,
            initial_option=incident.incident_priority.name,
            project_id=incident.project.id,
        ),
        incident_severity_select(
            db_session=db_session,
            initial_option=incident.incident_severity.name,
            project_id=incident.project.id,
        ),
        tag_multi_select(
            action_id=IncidentUpdateActionIds.tags,
            block_id=IncidentUpdateBlockIds.tags,
            initial_options=[t.name for t in incident.tags],
        ),
    ]

    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=IncidentUpdateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(
    IncidentUpdateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_project_select_action(ack, body, client, context, db_session):
    ack()
    values = body["view"]["state"]["values"]

    selected_project_name = values[DefaultBlockIds.project_select][
        IncidentUpdateActions.project_select
    ]["selected_option"]["value"]

    project = project_service.get_by_name(
        db_session=db_session,
        name=selected_project_name,
    )

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update incident details.")]),
        title_input(initial_value=incident.title),
        description_input(initial_value=incident.description),
        resolution_input(initial_value=incident.resolution),
        project_select(
            db_session=db_session,
            initial_option=project.name,
            action_id=IncidentUpdateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option=incident.incident_type.name,
            project_id=project.id,
        ),
        incident_priority_select(
            db_session=db_session,
            initial_option=incident.incident_priority.name,
            project_id=project.id,
        ),
        incident_severity_select(
            db_session=db_session,
            initial_option=incident.incident_severity.name,
            project_id=project.id,
        ),
        tag_multi_select(
            initial_options=[t.name for t in incident.tags],
        ),
    ]

    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=IncidentUpdateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


async def handle_report_incident_command(ack, body, context, db_session, client):
    """Handles the report incident command."""

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="If you suspect an incident and need help, please fill out this form to the best of your abilities."
                )
            ]
        ),
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            action_id=IncidentReportActions.project_select,
            dispatch_action=True,
        ),
        tag_multi_select(
            action_id=IncidentReportActionIds.tags,
            block_id=IncidentReportBlockIds.tags,
        ),
    ]

    modal = Modal(
        title="Report Incident",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=IncidentReportActions.submit,
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)
