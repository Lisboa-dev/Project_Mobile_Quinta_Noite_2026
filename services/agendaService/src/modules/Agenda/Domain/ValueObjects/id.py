import uuid
from src.modules.agenda.domain.exceptions import InvalidIdComparisonException

class ID:

    id: str

    def __init__(self, id: str | None = None):
        self.id = id or str(uuid.uuid4())
        
    def __str__(self):
        return self.id
    
    @staticmethod
    def generate_id():
        return ID(str(uuid.uuid4()))
    
    def compare(self, other_id):
        if isinstance(other_id, ID):
            return self.id == other_id.id
        elif isinstance(other_id, str):
            return self.id == other_id
        else:
            raise InvalidIdComparisonException(
                "Invalid ID type for comparison",
                {"other_id_type": type(other_id).__name__},
            )
