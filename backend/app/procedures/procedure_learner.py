""" Procedure learning implementation for NFM-X """

class ProcedureLearner:
    def __init__(self, procedure_store):
        self.procedure_store = procedure_store
    
    def learn_from_attempt(self, task, procedure_used, result, evaluation):
        return {"learned": True}
    
    def update_procedure_from_result(self, procedure_id, result):
        return self.procedure_store.get_procedure(procedure_id)
    
    def create_procedure_from_patterns(self, patterns):
        return None