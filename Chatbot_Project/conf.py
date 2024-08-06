from singleton_decorator import singleton



@singleton
class Config:
    def __init__(self):
        pass
    
    @property
    def Path(bot_id):
        return f'./RasaData/{bot_id}'