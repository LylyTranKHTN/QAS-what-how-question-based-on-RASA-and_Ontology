import argparse
import logging

from policy import AdobePolicy
from rasa_core import utils
from rasa_core.agent import Agent
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.policies.form_policy import FormPolicy

logger = logging.getLogger(__name__)

def train_dialogue(domain_file="adobe_domain.yml",
                   model_path="models/dialogue",
                   training_data_file="data/stories.md"):
    fallback = FallbackPolicy(fallback_action_name="action_default_fallback",
                              core_threshold=0.3,
                              nlu_threshold=0.3)
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=5),
                            AdobePolicy(epochs=200, batch_size=32,
                                             validation_split=0.2,
                                             max_history=4),
                            fallback,
                            FormPolicy()])

    training_data = agent.load_data(training_data_file)
    agent.train(
        training_data
    )

    agent.persist(model_path)
    return agent


def train_nlu():
    from rasa_nlu.training_data import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer

    training_data = load_data('data/nlu_data.md')
    trainer = Trainer(config.load("configs/nlu_tensorflow.yml"))
    trainer.train(training_data)
    model_directory = trainer.persist('models/nlu/',
                                      fixed_model_name="current")

    return model_directory


if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
        description='starts the bot')

    parser.add_argument(
        'task',
        choices=["train-nlu", "train-dialogue", "run"],
        help="what the bot should do - e.g. run or train?")
    task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu()
    elif task == "train-dialogue":
        train_dialogue()