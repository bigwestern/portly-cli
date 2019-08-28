import sys

this_module = sys.modules[__name__]

config = None
args = None

def set_derived_defaults(args, config):
    if 'query' in args and args.query is None:
        args.query = "owner:%s" % (config.get_owner_by_env(args.env))
    return args

def init(args, config):
    this_module.args = set_derived_defaults(args, config)
    this_module.config = config

