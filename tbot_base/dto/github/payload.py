from pydantic import BaseModel


class GithubWebhook(BaseModel):
    ref: str


class PushWebhook(GithubWebhook):
    pass


class BaseRefModel(BaseModel):
    ref: str


class PullRequestModel(BaseModel):
    base: BaseRefModel


class PullRequestWebhook(BaseModel):
    action: str
    pull_request: PullRequestModel
