# models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    comments = relationship("Comment", back_populates="user")


class Project(Base):
    __tablename__ = "projects"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String,  nullable=False)
    description = Column(String,  nullable=False)

    comments = relationship(
        "Comment",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True
    )



class Comment(Base):
    __tablename__ = "comments"
    id         = Column(Integer, primary_key=True)
    content    = Column(String, nullable=False)
    project_id = Column(Integer,
                        ForeignKey("projects.id", ondelete="CASCADE"),
                        nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="comments")
    user    = relationship("User",    back_populates="comments")



