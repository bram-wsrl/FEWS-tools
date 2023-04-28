def ns(tag, namespace=None):
    '''
    Prepend {namespace} to tag
    '''
    if namespace is None:
        return tag
    return f'{{{namespace}}}{tag}'
