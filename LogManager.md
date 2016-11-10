# JSON structure

Structure of `self.server_map` and `self.channel_map`, as well as `servers.json` and `channels.json`, will look like this:

### `servers.json`
```python
{
    server_0.id: {
        'name': server_0.name   # changes dynamically
    }

    server_1.id: {
        'name': server_1.name
    }

    ...
}
```

### `channels.json`
```python
{
    channel_0.id: {
        'name': channel_0.name                # changes dynamically
        'server_id': channel_0.server.id      # (of parent Server); should never change
        'server_name': channel_0.server.name  # (of parent Server)
    }

    channel_1.id: {
        'name': channel_1.name
        'server_id': channel_1.server.id
        'server_name': channel_1.server.name
    }

    ...
}
```
