from app.modules.PSM.repositories.repository import Repository
class Service():

    def __init__(self, repository : Repository, transform_model_to_dict, 
                 transform_dict_to_model):
        self.repository = repository
        #Each service should define its transformations
        self.transform_model_to_dict = transform_model_to_dict
        self.transform_dict_to_model = transform_dict_to_model

    def create(self, model_dict):
        model = self.transform_dict_to_model(model_dict)
        self.repository.add(model)

    def get(self, m_id):
        model = self.repository.get(m_id)
        return self.transform_model_to_dict(model)
    
    def get_all(self, page_no=1, page_size=10):
        limit = page_size
        offset = (page_no-1)*page_size
        model_list = self.repository.get_all(limit, offset)
        return self.__transform_model_list(model_list)
    
    def update(self,m_id, updated_dict):
        model = self.transform_dict_to_model(updated_dict)
        self.repository.update(m_id, model)

    def delete(self, m_id):
        self.repository.remove(m_id)
    

    def __transform_model_list(self, model_list):
        dict_list = []
        for model in model_list:
            dict_list.append(self.transform_model_to_dict(model))
        return dict_list

