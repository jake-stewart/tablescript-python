from tbl_token_type import TokenType

class Token:
    type: TokenType;
    value: str | None;

    def __init__(self, tokenType, value=None):
        self.type = tokenType;
        self.value = value;

    def __repr__(self):
        tokenType = str(self.type).replace("TokenType.", "");
        if self.value is not None:
            return "Token(%s, '%s')" % (tokenType, self.value);
        else:
            return "Token(%s)" % tokenType;

    def __str__(self):
        return repr(self);

