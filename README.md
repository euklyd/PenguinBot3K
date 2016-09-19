# About Arcbot
Arcbot is an extensible chatbot written entirely in Python, inspired by Err and Hubot projects.
The goal of Arcbot is to provide a simple to extend bot that can be used with many different chat services like Slack, Hipchat, Discord, IRC, Campire, etc.

Arcbot is open source software and released under the GPL v3 license. See LICENCE.txt for more info.

# Installing / Running
Everything about Arcbot is self contained, meaning that the entire bot is shipped and you run it from there.

### Running
1. Clone this repo
2. Fill out the `conf/settings.conf` file with your config settings
3. You must install the packages found in `REQUIREMENTS.txt`. Try doing `pip -r REQUIREMENTS.txt`
4. Run the entry point `bot.py` with Python 3
5. You're good to go!

# Bot Architecture

### Connectors
**Connectors** are what allow Arcbot to talk to the chat server. Every connector is subclassed from `core/connector.py`, which is the interface that the bot uses for the connector.

Since each chat provider has a different API, the internals of the connector will likely vary greatly; but must implement the abstract methods found in `core/connector.py` in order to function with the bot.

Currently, Arcbot only supports the unoffical Discord API connector. A full API has yet to be released for Discord, this connector is based on reverse engineering.

More connector support is coming soon: (Slack, Hipchat, Gitter)

### Plugin System
Using the power of Python, Arcbot gets all of it's functionality from plugins. The plugin system takes care of all the annoying code behind the scenes, so the code in for plugin is minimal. A sample plugin can be found at `plugins/Sample.py`, a plugin can be either a single python file or a folder with many files (in this case the main class should be in __init__.py file).

Arcbot also ships with a few plugins to get you started.

### ACL's
**Access control lists** are a way to enforce security policies for users of the bot. You may not want everyone in the channel to be able to disable plugins, or have the bot start Jenkins builds, so this is a way to assign user access and restrict what commands they can use.

### Multi-threaded Design
Arcbot makes use of thread pools to do it's dirty work. The command and event systems both will offload their work to threaded workers; to allow the bot to handle a very large load at once. This has the added benefit of being extremely responsive. This feature is tuneable in `conf/settings.py`; so you can set it up to best utilize your particular CPU and RAM needs.

### More features coming soon
Arcbot is still in active development, and not all design choices have been made. There is still a host of features I want to add before considering it stable; things like: 
* Web hook listeners
* Web based UI to manage the bot
* Connectors for other chat providers

# Credits
Credit must be given to the developers behind Hubot and Err projects; a lot of this bot was inspired by those projects.
