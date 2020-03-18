class InternalServerError(Exception):
    def __str__(self):
        return 'Internal Server Error, could not retrieve content.'
