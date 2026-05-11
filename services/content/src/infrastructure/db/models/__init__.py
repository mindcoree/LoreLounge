# # First, import the base class
# # from .base import Base

# # # Then the associations (so they load before the main models)
# # from .associations import novel_genres, novel_tags, NovelTeam

# # # Then the references and commands
# # from .metadata import Genre, Tag
# # from .team import Team, TeamMember

# # # And finally, the main models that use all of the above
# # from .novel import Novel, Chapter

# # For easy importing elsewhere
# __all__ = [
# "Base",
# "Novel",
# "Chapter",
# "Team",
# "TeamMember",
# "Genre",
# "Tag",
# "NovelTeam",
# "novel_genres",
# "novel_tags",
# ]