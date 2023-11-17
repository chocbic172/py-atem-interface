from __future__ import annotations
from abc import ABC, abstractmethod
import struct

class BufferException(Exception):
    """Base class for any atem buffer related errors"""
    pass

class PacketABC(ABC):
    """Abstract class representing all ATEM command packets"""

    @classmethod
    @abstractmethod
    def from_bytes(cls, packet):
        """Parse a set of bytes to form this class"""
        pass

    def to_bytes(self):
        """Convert the information in the class into a set of bytes"""
        pass

class PacketBuffer(object):
    """Provides helper functions for interfacing with binary
    packet buffers
    """
    _BYTE_ORDER = '!' # Network byte order (big-endian)

    def __init__(self, length_bytes: int) -> None:
        """Create a buffer of length `length_bytes`

        Args:
            length_bytes: length of buffer in bytes
        """
        self.size_bytes = length_bytes
        self.buffer = bytearray(length_bytes)

    @classmethod
    def from_bytes(cls, packet: bytes) -> PacketBuffer:
        """Create a buffer object from packet `packet`

        Args:
            packet: packet as bytes
        """
        cls.size_bytes = len(packet)
        cls.buffer = packet
        return cls

    def _get_struct_format_char(self, bits: int, signed: bool) -> str:
        """Get struct format character for struct.pack / struct.unpack

        See: https://docs.python.org/3/library/struct.html#format-characters
        Also: https://github.com/clvLabs/PyATEMMax for original implementation
        """
        format_char = ''

        if bits == 8:
            format_char = 'b'
        elif bits == 16:
            format_char = 'h'
        elif bits == 32:
            format_char = 'l'
        elif bits == 64:
            format_char = 'q'
        else:
            raise BufferException("_get_struct_format_char(): Invalid number"
                                  f"of bits ({bits}) requested")

        if not signed:
            format_char = format_char.upper()

        format_str = f"{self._BYTE_ORDER}{format_char}"

        return format_str

    def write_int(self, offset_bytes: int, value: int, bits: int, signed: bool=False) -> None:
        """Write an integer

        Args:
            offset_bytes: position in the buffer to write integer to
            value: value of the integer to be written
            bits: length of integer to be written in bits (must be a factor of 8)
            signed: is the integer signed (i.e. can it be <0)

        Raises:
            BufferException: Raised on input of invalid data
        """
        num_bytes = int(bits / 8)
        if (0 < offset_bytes) and (offset_bytes > (self.size_bytes - num_bytes)):
            raise BufferException(f"Not enough room in buffer to write {bits}bit"
                                  f" integer at offset {offset_bytes}.")

        struct_format = self._get_struct_format_char(bits, signed)
        struct.pack_into(struct_format, self.buffer, offset_bytes, value)

    def read_int(self, offset_bytes: int, bits: int, signed: bool=False) -> int:
        """Read an integer

        Args:
            offset_bytes: position in the buffer to read the integer from
            bits: length of integer to be read in bits (must be a factor of 8)
            signed: is the integer signed (i.e. can it be <0)

        Raises:
            BufferException: Raised on input of invalid data

        Returns:
            int - requested integer from buffer
        """
        num_bytes = int(bits / 8)
        if (0 < offset_bytes) and (offset_bytes > (self.size_bytes - num_bytes)):
            raise BufferException(f"Not enough room in buffer to read {bits}bit"
                                  f" integer at offset {offset_bytes}.")

        struct_format = self._get_struct_format_char(bits, signed)
        return struct.unpack_from(struct_format, self.buffer, offset_bytes)[0]

    def read_flag(self, offset_bytes: int, bitfield_len_bits: int, bit_position: int) -> bool:
        """Reads a flag from a bitfield in the buffer

        Args:
            offset_bytes: position of the bitfield in the buffer
            bitfield_len_bits: length of bitfield containing flag
            bit_position: location of flag bit within bitfield

        Returns:
            bool - whether requested flag bit is high
        """
        bitfield = self.read_int(offset_bytes, bitfield_len_bits)
        flag_bit = bitfield & (1<<bit_position)
        return True if flag_bit else False

    def write_flag(self, offset_bytes: int, bitfield_len_bits: int, bit_position: int, value: bool) -> None:
        """Writes a flag to a bitfield in the buffer

        Args:
            offset_bytes: position of the bitfield in the buffer
            bitfield_len_bits: length of bitfield containing flag
            bit_position: location of flag bit within bitfield
            value: request value of the bit to be written
        """
        bitfield = self.read_int(offset_bytes, bitfield_len_bits)

        if value:
            adjusted_bitfield = bitfield | (1<<bit_position)
        else:
            adjusted_bitfield = bitfield & ~(1<<bit_position)

        self.write_int(offset_bytes, adjusted_bitfield, bitfield_len_bits)

    def read_float(self, offset_bytes: int, bits: int, factor: int, signed: bool = False) -> float:
        """Reads a float

        Floats are calculated by diving the integer at the specified position
        within the buffer by 10^X, where X is the specified factor,

        Args:
            offset_bytes: position of float in the buffer
            bits: length of data to be read in bits
            factor: division factor when casting data to float
            signed: is the float signed (i.e. can the value be <0)

        Returns:
            float - requsted float from buffer
        """
        raw_data = self.read_int(offset_bytes, bits, signed)
        final_float = raw_data / (10**factor)
        return final_float

    def write_float(self, offset_bytes: int, bits: int, factor: int, value: int, signed: bool = False):
        """Writes a float

        Floats are stored by multiplying the float by 10^X (where X is the
        specified factor) and casting to an integer.

        Args:
            offset_bytes: position of float in the buffer
            bits: length of packed data to be written in bits
            value: float value to be written
            factor: multiplication factor when packing data into an int
            signed: is the float signed (i.e. can the value be <0)
        """
        packed_int = int(value * (10**factor))
        self.write_int(offset_bytes, packed_int, bits, signed)
    
    def read_string(self, offset_bytes: int, len_bytes: int) -> str:
        """Reads a string

        Args:
            offset_bytes: position of float in the buffer
            bytes: length of string to be written in bytes
        
            Return:
                str - requested string
        """
        encoded_str = self.buffer[offset_bytes:offset_bytes+len_bytes]
        return encoded_str.decode('utf8').rstrip('\x00')
    
    def write_string(self, offset_bytes: int, len_bytes: int, string: str):
        """Writes a string

        Args:
            offset_bytes: position of float in the buffer
            bytes: length of string to be written in bytes
            string: string to write
        """
        encoded_str = string.encode("utf8", "ignore")
        str_buffer = encoded_str + bytes([0 for _ in range(len_bytes)])
        trimmed_str_buffer = str_buffer[:len_bytes]
        self.buffer[offset_bytes:offset_bytes+len_bytes] = trimmed_str_buffer
