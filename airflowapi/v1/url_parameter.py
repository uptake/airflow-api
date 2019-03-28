
class APIParam(object):

    def __init__(
            self,
            name, param_help,
            data_type=None, choices=None, action=None, required=False, default=None, location=None, example=None
    ):
        self.name = name
        self.data_type = data_type
        self.param_help = param_help
        self.choices = choices
        self.action = action
        self.required = required
        self.default = default
        self.location = location
        self.example = example
