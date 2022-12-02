@app.command(
    SlackConversationConfiguration.slack_command_add_timeline,
    middleware=[command_context_middleware, db_middleware],
)
async def handle_add_timeline_event_command(ack, body, respond, client, context, db_session):
    """Handles the add timeline event command."""
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to add an event to the incident timeline.")]),
        datetime_picker_input(),
        description_input(),
    ]


    modal = Modal(title="Add Timeline Event", blocks=blocks, submit="Add", close="Close", callback_id=AddTimelineActions.submit, private_metadata=context["subject"].json()).build()

    await = client.views_open(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal
    )
