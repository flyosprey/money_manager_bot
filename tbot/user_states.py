from collections import defaultdict

from tbot.enums.users import UserStates

USERS_STATE = defaultdict(dict)
CREDENTIALS = defaultdict(dict)


def set_user_state(user_id: int, state: UserStates):
    USERS_STATE[user_id]["state"] = state


def get_user_state(user_id: int):
    return USERS_STATE.get(user_id, {}).get("state", UserStates.IDLE)
