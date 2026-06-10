import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from openai import OpenAI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

openai_api_key = "SUBSTITUA-POR-SUA-API-KEY-DA-OPENAI"

client = OpenAI(api_key=openai_api_key, timeout=12.0)

MODEL = "gpt-4o-mini"
MAX_QUERY_CHARS = 600
MAX_RESPONSE_TOKENS = 450
MAX_TURNS_PER_SESSION = 8
MAX_HISTORY_MESSAGES = 6

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "Você é uma assistente muito útil. Responda de forma clara, segura "
        "e concisa em Português do Brasil. Evite respostas longas, porque "
        "elas serão faladas por uma Alexa."
    ),
}


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = (
            "Bem vindo ao Chat 'Gepetê Quatro' da 'Open ei ai'! Qual a sua pergunta?"
        )

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots or {}
        query_slot = slots.get("query")
        query = query_slot.value.strip() if query_slot and query_slot.value else ""

        if not query:
            speak_output = "Não entendi sua pergunta. Pode repetir?"
            return (
                handler_input.response_builder.speak(speak_output)
                .ask(speak_output)
                .response
            )

        session_attributes = handler_input.attributes_manager.session_attributes
        turn_count = session_attributes.get("turn_count", 0)

        if turn_count >= MAX_TURNS_PER_SESSION:
            speak_output = (
                "Esta conversa atingiu o limite de perguntas. "
                "Abra a skill de novo para começar uma nova sessão."
            )
            return handler_input.response_builder.speak(speak_output).response

        response = generate_gpt_response(query, session_attributes)
        session_attributes["turn_count"] = turn_count + 1
        handler_input.attributes_manager.session_attributes = session_attributes

        return (
            handler_input.response_builder.speak(response)
            .ask("Você pode fazer uma nova pergunta ou falar: sair.")
            .response
        )


def generate_gpt_response(query, session_attributes):
    if len(query) > MAX_QUERY_CHARS:
        return "Sua pergunta ficou longa demais. Tente fazer uma pergunta mais curta."

    try:
        history = session_attributes.get("messages", [])
        if not isinstance(history, list):
            history = []

        history.append({"role": "user", "content": query})
        request_messages = [SYSTEM_MESSAGE] + history[-MAX_HISTORY_MESSAGES:]

        response = client.chat.completions.create(
            model=MODEL,
            messages=request_messages,
            max_tokens=MAX_RESPONSE_TOKENS,
            temperature=0.6,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session_attributes["messages"] = history[-MAX_HISTORY_MESSAGES:]

        return reply
    except Exception:
        logger.error("Erro ao gerar resposta da OpenAI", exc_info=True)
        return "Desculpe, não consegui gerar uma resposta agora. Tente novamente em alguns instantes."


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Como posso te ajudar?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Até logo!"

        return handler_input.response_builder.speak(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, não consegui processar sua solicitação."

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
