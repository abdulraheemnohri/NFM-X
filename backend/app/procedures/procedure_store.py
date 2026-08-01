""" Procedure storage implementation for NFM-X """

class ProcedureStore:
    def __init__(self):
        self.procedures = {}
    
    def store_procedure(self, procedure_id, name, steps, success_rate=0.0):
        self.procedures[procedure_id] = {
            "id": procedure_id, "name": name, "steps": steps,
            "success_rate": success_rate, "execution_count": 0, "version": 1
        }
        return self.procedures[procedure_id]
    
    def get_procedure(self, procedure_id):
        return self.procedures.get(procedure_id)
    
    def update_procedure(self, procedure_id, updates):
        if procedure_id in self.procedures:
            self.procedures[procedure_id].update(updates)
        return self.procedures.get(procedure_id)