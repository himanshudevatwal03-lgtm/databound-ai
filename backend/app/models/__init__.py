"""
models package

Importing each model module here (even though nothing else in this file
uses the name directly) ensures SQLAlchemy's Base.metadata knows about
every table before app.main calls Base.metadata.create_all(). Forgetting
to import a new model here is a classic bug: the model works fine in code
but its table silently never gets created.
"""

from app.models.user import User  # noqa: F401
