import yaml


class Config:
    def __init__(self):
        import os

        # 获取当前 config.py 所在目录
        config_path = os.path.join(os.path.abspath("./"), "config.yaml")

        with open(config_path, 'r') as file:
            _config = yaml.safe_load(file)
            self.server = _config['server']
            self.ocr = _config['ocr']


config = Config()
