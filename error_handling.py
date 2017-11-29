from flask_socketio import emit
import logging

class ErrorHandler:
    @staticmethod
    def game_code_dne(event, game_code):
        error_msg = """Game code does not exist. Please create a new game."""
        logging.warn('EVENT "%s" %s %s', event, game_code, error_msg)
        emit('error', error_msg)
