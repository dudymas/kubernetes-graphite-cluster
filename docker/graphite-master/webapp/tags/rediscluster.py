from graphite.tags.redis import RedisTagDB

class RedisClusterDB(RedisTagDB):
  """
  Stores tag information in a Redis database.

  Keys used are:

  .. code-block:: none

    series                    # Set of all paths
    series:<path>:tags        # Hash of all tag:value pairs for path
    tags                      # Set of all tags
    tags:<tag>:series         # Set of paths with entry for tag
    tags:<tag>:values         # Set of values for tag
    tags:<tag>:values:<value> # Set of paths matching tag/value

  """
  def __init__(self, settings, *args, **kwargs):
    super(RedisTagDB, self).__init__(settings, *args, **kwargs)

    from rediscluster import RedisCluster
    startup_nodes = [{"host": settings.TAGDB_REDIS_HOST, "port": settings.TAGDB_REDIS_PORT}]

    self.r = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)