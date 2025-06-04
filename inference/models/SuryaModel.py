from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict


class SuryaModel:

    def __init__(self):
        config = {
            "force_ocr": False,
            "use_llm": False
        }
        self.config_parser = ConfigParser(config)
        self.models = {}

    def load_model(self, device, dtype, pid):
        self.models[pid] = PdfConverter(
            artifact_dict=create_model_dict(
                device=device,
                dtype=dtype),
            config=self.config_parser.generate_config_dict(),
        )


suryaModel = SuryaModel()

