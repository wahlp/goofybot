development requires:
- python >=3.9
- linux/wsl for ssl with planetscale
- [gifsicle](https://github.com/kohler/gifsicle) (optional, required only if locally running command `/meme gif` with compression set to true)

`.env` requires secrets from:
- [discord](https://discordpy.readthedocs.io/en/stable/discord.html) 
- [planetscale](https://planetscale.com/docs/tutorials/connect-any-application)

deployment requires:
- aforementioned secrets, but put into parameter store on aws (see [here](/src/lib/envloader.py) for paths)

wishlist:
- create opt-out feature to exclude users from message tracking

assumptions:
- this bot will only run on 1 server
- for emoji reaction tracking, messages can be deleted with reactions attached. when this happens, the reaction entry is still kept