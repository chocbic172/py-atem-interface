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
