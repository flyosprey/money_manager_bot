import enum


class SettingsStates(enum.Enum):
    IDLE = 0
    AWAITING_LABEL = 1
    ADD_LABEL = 2
