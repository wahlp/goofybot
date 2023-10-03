requires:
- python >3.6
- linux/wsl (for ssl with planetscale)
- gifsicle (optional, required only if locally running command `/meme gif`)

`.env` requires secrets from:
- [discord](https://discordpy.readthedocs.io/en/stable/discord.html) 
- [planetscale](https://planetscale.com/docs/tutorials/connect-any-application)

wishlist:
- create opt-out feature to exclude users from message tracking

assumptions:
- this bot will only run on 1 server
- for emoji reaction tracking, messages can be deleted with reactions attached. when this happens, the reaction entry is still kept