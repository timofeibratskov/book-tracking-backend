class UserError(Exception):
    pass

class UserNotFoundError(UserError):
    def __init__(self, user_id: str | None = None):
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")

class EmailAlreadyExistsError(UserError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email '{email}' already exists")

class InvalidCredentialsError(UserError):
    def __init__(self):
        super().__init__("Invalid email or password")

class RepositoryError(UserError):
    def __init__(self, message: str = "Database operation failed", original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(f"Repository error: {message}")

class ServiceError(UserError):
    def __init__(self, message: str = "An unexpected service error occurred", original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(f"Service error: {message}")
