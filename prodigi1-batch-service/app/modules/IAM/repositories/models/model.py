class Model:
    def __init__(self,table):
        
        self.table = table
        
    def get_dict(self):
        return(self.__dict__)