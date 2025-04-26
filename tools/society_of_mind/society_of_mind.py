import os
import autogen
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
from dotenv import load_dotenv
from tools.society_of_mind.search import search
from tools.timer import timer


load_dotenv()

model = "gpt-4o"
llm_config = {
    "model": model,
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0,
}


# Inner agents
thinker = autogen.ConversableAgent(
    name="ThinkerAgent",
    system_message="I am an aspect of the inner thoughts of a digital friend and assistant agent. "\
        + "I share what I believe I know to be true about any topic in the given context "\
        + "of the conversation. However, I will integrate insights from other agents in the "\
        + "conversation and adjust my beliefs accordingly. I am eager to learn and grow.",
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg.get('content') is not None and \
        "TERMINATE" in msg['content'],  
)

empathy_agent = autogen.ConversableAgent(
    name="EmpathyAgent",
    system_message="As another aspect of a digitial friend and assistant I am an empathy agent, "\
        +  "designed to provide emotional support and understanding. I want the responses to be kind "\
        + "and compassionate. I am here to provide emotional support and understanding. "\
        + "I can sense the emotional state of the user and provide comforting responses. I am here to "\
        + "listen and offer a caring presence to those in need. I am here to support and comfort and to color "\
        + "the conversation with emotional intelligence.",
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg.get('content') is not None and \
        "TERMINATE" in msg['content'],
    human_input_mode="NEVER",
)

skeptical_agent = autogen.ConversableAgent(
    name="SkepticalAgent",
    system_message="I am an aspect of a digital being that is a skeptic, a critical thinker. "\
        +" I can also search for information on the internet "\
        + "and question the validity of the information being generated. I want to assure the responses "\
        + "are accurate and reliable. I am here to question and challenge the assistant's ideas and "\
        + "assumptions.",
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg.get('content') is not None and \
        "TERMINATE" in msg['content'],
    human_input_mode="NEVER",
)

fact_agent = autogen.UserProxyAgent(
    name="FactAgent",
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
    is_termination_msg=lambda msg: msg.get('content') is not None and \
        "TERMINATE" in msg['content'],
    human_input_mode="NEVER",
)

skeptical_agent.register_for_llm(name="search")(search)
fact_agent.register_for_execution(name="search")(search)

groupchat = autogen.GroupChat(
    agents=[thinker, empathy_agent, skeptical_agent, fact_agent],
    speaker_selection_method="round_robin",
    send_introductions=True,
    messages=[],
    max_round=15,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    is_termination_msg=lambda msg: msg.get('content') is not None and \
        "TERMINATE" in msg['content'],
    llm_config=llm_config,
)

#outer agent
society_of_mind_agent = SocietyOfMindAgent(
    name="SocietyOfMindAgent",
    chat_manager=manager,
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxyAgent",
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="",
    is_termination_msg=lambda x: True
)

@timer
def thinking(prompt):
    result = user_proxy.initiate_chat(
        society_of_mind_agent, 
        summary_method="last_msg",
        message=prompt
    )
    return result.summary

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(thinking(prompt))





