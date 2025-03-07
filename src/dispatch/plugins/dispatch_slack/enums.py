from dispatch.enums import DispatchEnum


class SlackAPIGetEndpoints(DispatchEnum):
    conversations_history = "conversations.history"
    conversations_info = "conversations.info"
    users_conversations = "users.conversations"
    users_info = "users.info"
    users_lookup_by_email = "users.lookupByEmail"
    users_profile_get = "users.profile.get"


class SlackAPIPostEndpoints(DispatchEnum):
    bookmarks_add = "bookmarks.add"
    chat_post_message = "chat.postMessage"
    chat_post_ephemeral = "chat.postEphemeral"
    chat_update = "chat.update"
    conversations_archive = "conversations.archive"
    conversations_create = "conversations.create"
    conversations_invite = "conversations.invite"
    conversations_rename = "conversations.rename"
    conversations_set_topic = "conversations.setTopic"
    conversations_unarchive = "conversations.unarchive"
    pins_add = "pins.add"


class SlackAPIErrorCode(DispatchEnum):
    CHANNEL_NOT_FOUND = "channel_not_found"
    CHANNEL_NOT_ARCHIVED = "not_archived"
    FATAL_ERROR = "fatal_error"
    USER_IN_CHANNEL = "user_in_channel"
    USER_NOT_IN_CHANNEL = "user_not_in_channel"
    USER_NOT_FOUND = "user_not_found"
    VIEW_NOT_FOUND = "not_found"  # Could not find corresponding view for the provided view_id
    VIEW_EXPIRED = "expired_trigger_id"  # The provided trigger_id is no longer valid
