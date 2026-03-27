from fastapi import HTTPException


class TaskNotFoundException(HTTPException):
    def __init__(self):
        
        self.status_code = 404
        self.detail = {
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": "Task not found"
            }
        }
        super().__init__(status_code=self.status_code, detail=self.detail)

class CommentNotFoundException(HTTPException):
    def __init__(self):
        self.status_code = 404
        self.detail = {
            "error": {
                "code": "COMMENT_NOT_FOUND",
                "message": "Comment not found"
            }
        }
        super().__init__(status_code=self.status_code, detail=self.detail)