import pytest

from .packet import PacketBuffer, BufferException

class TestPacketBuffer:
    def test_create_class_from_bytes(self):
        input_bytes = (12).to_bytes(10)
        buf = PacketBuffer.from_bytes(input_bytes)

        assert buf.size_bytes == 10
        assert int.from_bytes(buf.buffer[0:10]) == 12

    def test_write_int(self):
        buf = PacketBuffer(8)

        buf.write_int(offset_bytes=0, value=0, bits=8)
        assert int.from_bytes(buf.buffer[0:1]) == 0

        buf.write_int(offset_bytes=1, value=127, bits=8)
        assert int.from_bytes(buf.buffer[1:2]) == 127

        buf.write_int(offset_bytes=2, value=12, bits=8)
        assert int.from_bytes(buf.buffer[2:3]) == 12

        buf.write_int(offset_bytes=3, value=-2, bits=8, signed=True)
        assert int.from_bytes(buf.buffer[3:4], signed=True) == -2

        with pytest.raises(BufferException):
            buf.write_int(offset_bytes=100, value=0, bits=8)

    def test_read_int(self):
        buf = PacketBuffer(8)

        buf.buffer[0:1] = (0).to_bytes(8)
        assert buf.read_int(offset_bytes=0, bits=8) == 0

        buf.buffer[1:2] = (127).to_bytes(1)
        assert buf.read_int(offset_bytes=1, bits=8) == 127

        buf.buffer[2:3] = (12).to_bytes(1)
        assert buf.read_int(offset_bytes=2, bits=8) == 12

        buf.buffer[3:4] = (-2).to_bytes(1, signed=True)
        assert buf.read_int(offset_bytes=3, bits=8, signed=True) == -2

        with pytest.raises(BufferException):
            buf.read_int(offset_bytes=100, bits=8)

    def test_get_struct_format_char(self):
        buf = PacketBuffer(0)

        buf._get_struct_format_char(8, False) == '!b'
        buf._get_struct_format_char(8, True) == '!B'

        buf._get_struct_format_char(16, False) == '!h'
        buf._get_struct_format_char(16, True) == '!H'

        buf._get_struct_format_char(32, False) == '!l'
        buf._get_struct_format_char(32, True) == '!L'

        buf._get_struct_format_char(64, False) == '!q'
        buf._get_struct_format_char(64, True) == '!Q'

        with pytest.raises(BufferException):
            buf._get_struct_format_char(23, False)

    def test_write_flag(self):
        buf = PacketBuffer(8)

        buf.write_flag(offset_bytes=0, bitfield_len_bits=8,
                       bit_position=4, value=True)
        assert buf.read_int(offset_bytes=0, bits=8) == 0b00010000

        buf.write_flag(offset_bytes=0, bitfield_len_bits=8,
                       bit_position=4, value=False)
        assert buf.read_int(offset_bytes=0, bits=8) == 0b000000000

        buf.write_flag(offset_bytes=1, bitfield_len_bits=8,
                       bit_position=7, value=True)
        assert buf.read_int(offset_bytes=1, bits=8) == 0b10000000

    def test_read_flag(self):
        buf = PacketBuffer(8)

        buf.buffer[0:1] = (0b10000001).to_bytes(1)
        assert buf.read_flag(offset_bytes=0, bitfield_len_bits=8,
                             bit_position=7)
        assert buf.read_flag(offset_bytes=0, bitfield_len_bits=8,
                             bit_position=0)
        assert not buf.read_flag(offset_bytes=0, bitfield_len_bits=8,
                                 bit_position=2)
    
    def test_write_float(self):
        buf = PacketBuffer(8)

        buf.write_float(offset_bytes=0, bits=8, factor=2, value=1.21)
        assert int.from_bytes(buf.buffer[0:1]) == 121

        buf.write_float(offset_bytes=1, bits=8, factor=2, value=-1.21,
                        signed=True)
        assert int.from_bytes(buf.buffer[1:2], signed=True) == -121

    def test_read_float(self):
        buf = PacketBuffer(8)

        buf.buffer[0:1] = (121).to_bytes(1)
        assert buf.read_float(offset_bytes=0, bits=8, factor=2) == 1.21

        buf.buffer[1:2] = (-121).to_bytes(1, signed=True)
        assert buf.read_float(offset_bytes=1, bits=8, factor=2, signed=True)\
            == -1.21
    
    def test_write_string(self):
        buf = PacketBuffer(32)

        buf.write_string(offset_bytes=0, len_bytes=8, string="abcdefgh")
        assert buf.buffer[0:8].decode("utf8").rstrip('\x00') == "abcdefgh"

        buf.write_string(offset_bytes=8, len_bytes=8, string="abc")
        assert buf.buffer[8:16].decode("utf8").rstrip('\x00') == "abc"

        buf.write_string(offset_bytes=16, len_bytes=8, string="abcdefghij")
        assert buf.buffer[16:32].decode("utf8").rstrip('\x00') == "abcdefgh"
    
    def test_read_string(self):
        buf = PacketBuffer(32)

        buf.buffer[0:8] = "abcdefgh".encode('utf8')
        assert buf.read_string(offset_bytes=0, len_bytes=8) == "abcdefgh"

        buf.buffer[8:16] = "abc".encode('utf8')
        assert buf.read_string(offset_bytes=8, len_bytes=8) == "abc"

        buf.buffer[16:32] = "abcdefghijk".encode('utf8')
        assert buf.read_string(offset_bytes=16, len_bytes=8) == "abcdefgh"
