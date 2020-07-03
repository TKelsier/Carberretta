"""
MOD

Handles automatic mod systems:
    Profanity filter;
    Mention-spam preventer;
    Modmail system.

**Manual moderation is handled by S4, and thus is not included.**
"""


from discord.ext.commands import Cog


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


def setup(bot):
    bot.add_cog(Mod(bot))