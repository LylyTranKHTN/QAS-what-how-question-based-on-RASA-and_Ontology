from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.form_policy import FormPolicy
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy, AugmentedMemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.train import interactive
from rasa_core.utils import EndpointConfig

logger = logging.getLogger(__name__)

DOMAIN_FILE = 'adobe_domain.yml'
TRAINING_DATA_FILE = 'data/stories.md'
NLU_INTERPRETER = 'models/nlu/default/current'


def run_bot_online(interpreter,
                   domain_file,
                   training_data_file):
    action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")

    fallback = FallbackPolicy(fallback_action_name="action_default_fallback",
                              core_threshold=0.3,
                              nlu_threshold=0.3)


    agent = Agent(domain=domain_file,
                  policies=[MemoizationPolicy(max_history=6),
                            KerasPolicy(max_history=6, epochs=200),
                            fallback,
                            FormPolicy()],
                  interpreter=interpreter,
                  action_endpoint=action_endpoint)

    data = agent.load_data(training_data_file)
    agent.train(data)
    interactive.run_interactive_learning(agent, training_data_file)
    return agent


if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    nlu_interpreter = RasaNLUInterpreter(NLU_INTERPRETER)
    run_bot_online(interpreter=nlu_interpreter, domain_file=DOMAIN_FILE, training_data_file=TRAINING_DATA_FILE)
