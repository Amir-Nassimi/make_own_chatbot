from singleton_decorator import singleton



@singleton
class Config:
    def __init__(self):
        pass
    
    def Path(self, bot_id):
        return f'./RasaData/{bot_id}'