from dagster import solid, Field, Int, String
import redis

REDIS_CONFIG = {
    'password': Field(
        String,
        is_required=False,
        description='Redis password'
    ),
    'host': Field(
        String,
        is_required=False,
        default_value='localhost',
        description='Redis host'
    ),
    'port': Field(
        Int,
        is_required=False,
        default_value=6379,
        description='Redis port'
    ),
    'db': Field(
        Int,
        is_required=False,
        default_value=0,
        description='Redis DB'
    )
}

@solid(config_schema=REDIS_CONFIG)
def redis_set(context, key: String, value: String):
    r = redis.Redis(host=context.solid_config['host'],
        port=context.solid_config['port'], db=context.solid_config['db'],
        password=context.solid_config['password'])
    r.set(key, value)

@solid(config_schema=REDIS_CONFIG)
def redis_get(context, key: String) -> String:
    r = redis.Redis(host=context.solid_config['host'],
        port=context.solid_config['port'], db=context.solid_config['db'],
        password=context.solid_config['password'])
    return r.get(key)
