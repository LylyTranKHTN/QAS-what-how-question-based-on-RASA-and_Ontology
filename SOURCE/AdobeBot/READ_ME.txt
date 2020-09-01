B1: run action web hook


B2: run rasa core
python -m rasa_core.run --enable_api --nlu models/nlu/default/current --core models/dialogue --endpoints endpoints.yml --cors "*"

