class Repository():

    def __init__(self, session):
        self.session = session
        #Each repository should define its model_type
        self.model_type = None

    def get(self,m_id):
        """Get model from db 

        Args:
            model_type (Type of Model): Classname of model
            id (integer): id of the entity

        Returns:
            model: model 
        """  
        with self.session:      
            return self.session.query(self.model_type).filter_by(id=m_id).first()

    def get_all(self, limit=1000, offset=0):
        """Get all models from db 


        Returns:
            model_list: list of models
        """ 
        with self.session:       
            return self.session.query(self.model_type).limit(limit).offset(offset).all()

    def add(self, model):
        """Add model to db

        Args:
           model : model to be added to db

        Returns:
            model: model 
        """             
        self.session.add(model)
        self.session.commit()
        self.session.flush()
        return model
    
    def update(self,id,model):
        """Commit changes to models
        """
        self.session.query(self.model_type).filter_by(id=id).update(model)      
        self.session.commit()

    def commit(self):
        self.session.commit()

    def remove(self, m_id):
        """Remove mode from db

        Args:
            model_type (Type of Model): Classname of model
            id (integer): id of the entity
        """        
        self.session.query(self.model_type).filter_by(id=m_id).delete()
        self.session.commit()

    def bulk_insert(self, list_of_models):
        """Add multiple models to db

        Args:
           list_of_models : models to be added to db

        Returns:
            list_of_models: list of model
        """
        self.session.bulk_save_objects(list_of_models, return_defaults = True)
        self.session.commit()
        self.session.flush()
        return list_of_models
    
    def bulk_insert_mappings(self, list_of_mappings):
        """Add multiple models to db

        Args:
           list_of_mappings : dict models to be added to db

        Returns:
            list_of_models: list of model
        """
        self.session.bulk_insert_mappings(self.model_type, list_of_mappings)
        self.session.commit()
        self.session.flush()
        return list_of_mappings

    def filter_by(self, **filters):
        with self.session:
            return self.session.query(self.model_type).filter_by(**filters).first()
    
    def filter_by_many(self, **filters):
        with self.session:
            return self.session.query(self.model_type).filter_by(**filters).all()

    def add_or_update(self, model):
        """Add multiple models to db

        Args:
           list_of_models : models to be added to db

        Returns:
            model: added or updated model
        """
        model_id = model.id
        model_obj = self.get(model_id)

        if model_obj is None:
            return self.add(model)
        else:
            model_obj.update(model)
            self.session.commit()
            return model
