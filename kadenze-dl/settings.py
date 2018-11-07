import yaml


class Settings(object):
    def __init__(self):
        with open("configuration.yml", 'r') as configfile:
            self.config = yaml.load(configfile)
        self.login = self.config['kadenze']['login']
        self.password = self.config['kadenze']['password']
        self.path = self.config['download']['path']
        self.courses = self.config['download']['courses']
        self.video_format = self.config['download']['resolution']
        self.videos_titles = self.config['download']['videos_titles']
        self.selected_only = "all" not in self.courses

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance
