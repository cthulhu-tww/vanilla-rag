import yaml


class Config:
    def __init__(self):
        import os
        # 默认配置路径
        config_path = os.path.join(os.path.abspath(""), "config.yaml")
        with open(config_path, 'r') as file:
            _config = yaml.safe_load(file)
            self.milvus = _config['milvus']
            self.interface = _config['interface']
            self.mcp = _config['mcp']
            self.server = _config['server']


config = Config()
