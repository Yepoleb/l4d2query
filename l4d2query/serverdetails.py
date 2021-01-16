import dataclasses
from dataclasses import dataclass
import typing
import enum

import io
import socket
import time

from l4d2query.byteio import ByteReader, ByteWriter

DEFAULT_TIMEOUT = 3.0
DEFAULT_ENCODING = "utf-8"

class TokenType(enum.IntEnum):
    OBJECT = 0
    STRING = 1
    INT32 = 2
    FLOAT = 3
    PTR = 4
    WSTRING = 5
    COLOR = 6
    UINT64 = 7
    COMPILED_INT_BYTE = 8
    COMPILED_INT_0 = 9
    COMPILED_INT_1 = 10
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
    engine_build: int
    payload_size: int
    data: dict
    binary_data: bytes


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
    elif token_type == TokenType.INT32:
        value = reader.read_int32()
    elif token_type == TokenType.FLOAT:
        value = reader.read_float()
    elif token_type == TokenType.PTR:
        value = reader.read_uint32()
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
    elif token_type == TokenType.INT32:
        writer.write_int32(value)
    elif token_type == TokenType.FLOAT:
        writer.write_float(value)
    elif token_type == TokenType.PTR:
        writer.write_uint32(value)
    elif token_type == TokenType.UINT64:
        writer.write_uint64(value)
    else:
        raise NotImplementedError("Unknown item type: {}".format(token_type))

def decode_tokenpacket(packet_data, encoding):
    stream = io.BytesIO(packet_data)
    reader = ByteReader(stream, endian="<", encoding=encoding)
    packet = TokenPacket()
    packet.header = reader.read(8)
    packet.engine_build = reader.read_uint32()
    packet.payload_size = reader.read_uint32()
    reader.endian = ">" # yes, this is an endian switch in the middle of the packet
    root_token = read_token(reader)
    packet.data = root_token.value
    reader.read_uint8()
    binary_size = reader.read_uint32()
    packet.binary_data = reader.read(binary_size)
    return packet

def construct_serverdetails(timestamp, pingxuid):
    stream = io.BytesIO()
    writer = ByteWriter(stream, endian="<", encoding="utf-8")
    writer.write(b"\xff\xff\xff\xff\x00\x00\x00\x00") # header
    writer.write_uint32(2211) # engine_build
    writer.write_uint32(60) # payload_size
    writer.endian = ">"
    write_token(writer, TokenType.OBJECT, "InetSearchServerDetails", None)
    write_token(writer, TokenType.FLOAT, "timestamp", timestamp)
    write_token(writer, TokenType.UINT64, "pingxuid", pingxuid)
    write_token(writer, TokenType.END, None, None)
    write_token(writer, TokenType.END, None, None)
    writer.write_uint32(0) # binary size
    return bytes(stream.getbuffer())

def query_serverdetails(addr, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING):
    request_data = construct_serverdetails(timestamp=time.time(), pingxuid=0)
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.settimeout(timeout)
    s.sendto(request_data, addr)
    response_data = s.recv(65535)
    return decode_tokenpacket(response_data, encoding=encoding)
