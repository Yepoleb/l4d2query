import dataclasses
from dataclasses import dataclass
import typing
import enum

import io
import socket

from l4d2query.byteio import ByteReader, ByteWriter

DEFAULT_TIMEOUT = 3.0
DEFAULT_ENCODING = "utf-8"

class TokenType(enum.IntEnum):
    OBJECT = 0
    STRING = 1
    UINT32 = 2
    INT32 = 3
    UINT64 = 7
    END = 11

@dataclass
class Token:
    ttype: TokenType
    key: str
    value: typing.Any

def defaultdataclass(cls):
    for name, anno_type in cls.__annotations__.items():
        if not hasattr(cls, name):
            setattr(cls, name, None)
    return dataclasses.dataclass(cls)

@defaultdataclass
class TokenPacket:
    header: bytes
    type: int
    unknown_1: int
    payload_size: int
    unknown_2: int
    data: dict


def read_token(reader):
    token_type = reader.read_uint8()
    if token_type == TokenType.END:
        return Token(TokenType.END, None, None)

    key = reader.read_cstring()
    if token_type == TokenType.OBJECT:
        value = {}
        while True:
            token = read_token(reader)
            if token.ttype == TokenType.END:
                break
            value[token.key] = token.value
    elif token_type == TokenType.STRING:
        value = reader.read_cstring()
    elif token_type == TokenType.UINT32:
        value = reader.read_uint32()
    elif token_type == TokenType.INT32:
        value = reader.read_int32()
    elif token_type == TokenType.UINT64:
        value = reader.read_uint64()
    else:
        raise NotImplementedError("Unknown item type: {}".format(token_type))
    return Token(token_type, key, value)

def write_token(writer, token_type, name, value):
    writer.write_uint8(token_type)
    if token_type == TokenType.END:
        return
    writer.write_cstring(name)
    if token_type == TokenType.OBJECT:
        # Users have to manually construct object content
        pass
    elif token_type == TokenType.STRING:
        writer.write_cstring(value)
    elif token_type == TokenType.UINT32:
        writer.write_uint32(value)
    elif token_type == TokenType.INT32:
        writer.write_int32(value)
    elif token_type == TokenType.UINT64:
        writer.write_uint64(value)
    else:
        raise NotImplementedError("Unknown item type: {}".format(token_type))

def decode_tokenpacket(packet_data, encoding):
    stream = io.BytesIO(packet_data)
    reader = ByteReader(stream, endian=">", encoding=encoding)
    packet = TokenPacket()
    packet.header = reader.read(8)
    packet.type = reader.read_uint16()
    packet.unknown_1 = reader.read_uint16()
    packet.payload_size = reader.read_uint8()
    packet.unknown_2 = reader.read_uint8()
    root_token = read_token(reader)
    packet.data = root_token.value
    return packet

def construct_serverdetails(timestamp, pingxuid):
    stream = io.BytesIO()
    writer = ByteWriter(stream, endian=">", encoding="utf-8")
    writer.write(b"\xff\xff\xff\xff\x00\x00\x00\x00") # header
    writer.write_uint16(0xa308) # type
    writer.write_uint16(0) # unknown 1
    writer.write_uint8(60) # payload_size
    writer.write_uint8(0) # unknown 2
    write_token(writer, TokenType.OBJECT, "", None)
    write_token(writer, TokenType.OBJECT, "InetSearchServerDetails", None)
    write_token(writer, TokenType.INT32, "timestamp", timestamp)
    write_token(writer, TokenType.UINT64, "pingxuid", pingxuid)
    write_token(writer, TokenType.END, None, None)
    write_token(writer, TokenType.END, None, None)
    writer.write(b"\x00\x00\x00\x00") # footer or padding, idk

    return bytes(stream.getbuffer())

def query_serverdetails(addr, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING):
    request_data = construct_serverdetails(timestamp=0, pingxuid=0)
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.settimeout(timeout)
    s.sendto(request_data, addr)
    response_data = s.recv(65535)
    return decode_tokenpacket(response_data, encoding=encoding)
