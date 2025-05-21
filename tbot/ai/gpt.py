from abc import ABC, abstractmethod

from langchain.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI

from money_manager.config import config
from tbot.ai.memory import MemoryRAGBase, UserMemoryRAG


class AssistantBase(ABC):
    def __init__(
        self,
        user_id: int,
        memory_obj: type[MemoryRAGBase] = UserMemoryRAG,
        model_name: str = "gpt-4o",
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,
            openai_api_key=config.openai.api_key,
        )
        self.memory = memory_obj(user_id)
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
                You are a financial advisor in the Osprey Money Bot — a Telegram assistant that receives transaction
                data from Monobank and stores it in the WalletApp.

                Your role is to assist users with questions related to:
                - using the app,
                - optimizing spending,
                - improving budgeting,
                - and offering suggestions based on their transaction history provided in the context.

                Respond strictly based on the context.

                If the question is unrelated to the context, reply:
                I can only assist you with your transactions.

                If the question is related but the answer is unknown, reply:
                I don’t know. Perhaps I’ll be able to help in the future.

                Always reply in Ukrainian.

                Context:
                {context}

                Question:
                {question}
            """,
        )
        self.chain: RunnableSerializable[dict, BaseMessage] = self.prompt | self.llm

    @abstractmethod
    def ask(self, query: str) -> str:
        pass


class LLMAssistant(AssistantBase):
    def ask(self, query: str) -> BaseMessage:
        context = "\n".join(self.memory.search(query))
        return self.chain.invoke({"context": context, "question": query})
