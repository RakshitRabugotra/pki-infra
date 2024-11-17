import base64


class Certificate:

    def __init__(
        self,
        request_id: str,
        public_key: str,
        identifier: str,
        issued_by: str,
        issued_at: float,
        certificate_id: str,
        sign: bytes
    ):
        self.request_id = request_id
        self.public_key = public_key
        self.identifier = identifier
        self.issued_by = issued_by
        self.issued_at = issued_at
        self.certificate_id = certificate_id
        self.sign = sign

    def to_dict(self):
        return  {
            'request_id': self.request_id,
            'public_key': self.public_key,
            'identifier': self.identifier,
            'issued_by': self.issued_by,
            'issued_at': self.issued_at,
            'certificate_id': self.certificate_id,
            'sign': self.sign.hex()
        }

    @classmethod
    def from_dict(cls, certificate_like: dict[str, str | bytes | float]):
        return cls(
            request_id=certificate_like['request_id'],
            public_key=certificate_like["public_key"],
            identifier=certificate_like["identifier"],
            issued_by=certificate_like["issued_by"],
            issued_at=certificate_like["issued_at"],
            certificate_id=certificate_like["certificate_id"],
            sign=bytes.fromhex(certificate_like['sign']) if certificate_like.get('sign') is not None else None
        )
