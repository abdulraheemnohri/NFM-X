""" Skill matching implementation for NFM-X """

class SkillMatcher:
    def __init__(self, skill_store):
        self.skill_store = skill_store
    
    def match_skills(self, task_description, limit=5):
        all_skills = list(self.skill_store.skills.values())
        return sorted(all_skills, key=lambda x: self.calculate_match_score(x, task_description), reverse=True)[:limit]
    
    def calculate_match_score(self, skill, task_description):
        return 0.5