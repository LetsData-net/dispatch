import logging
from slack_bolt.adapter.socket_mode import SocketModeHandler

from dispatch.plugins.dispatch_slack.bolt import app


log = logging.getLogger(__name__)


def run_websocket_process(config):
    app._token = config.api_bot_token.get_secret_value()
    handler = SocketModeHandler(app, config.socket_mode_app_token.get_secret_value())
    handler.start()
