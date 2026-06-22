class InvalidMetaTypeError(Exception):
    """
    File is unreadable as its meta-type is incorrect. Eg. XML is given to a parser
    which expects JSON.
    """

    pass


class InvalidRecordError(Exception):
    """
    Record can be read by computer, but should not be parsed because it is
    invalid. One example would be a record whose coverage is negative.
    """

    pass


class SchemaFormatError(Exception):
    """
    Unable to render data in the correct schema. Eg. Expecting version 1, got version 2.
    """

    pass
