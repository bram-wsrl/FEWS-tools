def ns(tag, namespace=None):
    '''
    Prepend {namespace} to tag
    '''
    if namespace is None:
        return tag
    return f'{{{namespace}}}{tag}'


def add_loghandler(logger, handler, loglevel, formatter, **kwargs):
    '''
    Add loghandler, kwargs are passed to handler instance
    '''
    handler = handler(**kwargs)
    handler.setLevel(loglevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
