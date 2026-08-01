""" Skill learning implementation for NFM-X """

class SkillLearner:
    def __init__(self, skill_store):
        self.skill_store = skill_store
    
    def learn_skill(self, name, procedure, success_count=1):
        skill_id = f"skill_{len(self.skill_store.skills) + 1}"
        return self.skill_store.store_skill(skill_id, name, "", procedure)
    
    def reinforce_skill(self, skill_id):
        skill = self.skill_store.get_skill(skill_id)
        if skill:
            skill["success_count"] += 1
        return skill
    
    def get_skill_confidence(self, skill_id):
        skill = self.skill_store.get_skill(skill_id)
        if skill and skill["success_count"] > 0:
            total = skill["success_count"] + skill["failure_count"]
            return skill["success_count"] / total if total > 0 else 0
        return 0