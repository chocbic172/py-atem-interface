# Interface definitions

The interface is defined using several yaml files. These files are parsed and generated into a python interface. The library is written on top of the interface, which is baked into the package.

Note that the definitions include packets sent both from and to the device, allowing us to locally emulate a switcher.

## Examples

Below is an example of how to define an enum:

```
ATEMEnumName:
  _role: enum
  _bits: <size of enum when packed>
  _doc: <optional documentation>

  member1: enumeration
  member2: enumeration
  ...
```

Below is an example of how to define a command:

In this case, the `_role` mapping can be either `device2host_command` or `host2device_command`, depending on where the command is typically sent from. In most cases, the device will be the ATEM switcher.

There is further information on available types below.

```
ATEMCommandName:
  _role: [device2host/host2device]_command
  _bits: <size of packed command excl header>
  _cmd: <command name e.g. CPgI >
  _doc: <optional documentation>
  
  packet:
    - <name>: <type>
    - <name>: <type>
    ...
```

## Types

The interface defintion format requires its own set of types, which mirror similar types seen in C code with some subtle differences.

### Floating point numbers

Floating point numbers are not stored using the IEEE-754 standard as you might expect, but rather using integers that divided by a power of 10. For example, `1.012` would be stored as the integer `1012` when packed, then divided by 10^3 to get the actual value.

Hence, we define a set of types to represent these numbers. For example, `sfloat16_3` for example defines a float that can be calculated by taking a 16-bit signed integer and diving it by 10^3.

### Bitfields / Flags

In the protocol, a bitfield represents a list of booleans. Each flag within the bitfield can be labelled as in the example. Each boolean will be available from the interface, but the bitfield cannot be referred to. You do not need to label every bit in the bitfield, but the number of labels must not exceed the number of bits in the bitfield (i.e. a `bitfield8` can have no more than 8 labels).
```
bitfield8:
  - boolean1
  - boolean2
  ...
```

### Enums

To reference an enum in the interface, preface the name of the enum with the `enum`, then the name of the enum, AND the name of its module. For example, to reference the mix effect enum you would use the following:
```
packet:
  - mix_effect: enum mixeffect.ATEMMixEffect
```

|Type|C Type|Description|
|-|-|-|
|`bitfield8`|array|8-bit bitfield. Accompany with labels, as in the example [above](#Bitfields-/-Flags).|
|`bitfield16`|array|16-bit bitfield. Accompany with labels, as in the example [above](#Bitfields-/-Flags).|
|`bitfield32`|array|32-bit bitfield. Accompany with labels, as in the example [above](#Bitfields-/-Flags).|
|`bool`|bool|Boolean, casts any value > 0 to True|
|`enum`|int|Variable length enumeration (see [above](#enums) for how to use)|
|`sint8`|sint8|Signed 8-bit Integer|
|`sint16`|sint16|Signed 16-bit Integer|
|`sint32`|sint32|Signed 32-bit Integer|
|`sint64`|sint64|Signed 64-bit Integer|
|`sfloat8_X`|sfloat32|Signed 8-bit Integer, converted to float by dividing by 10^X|
|`sfloat16_X`|sint16|Signed 16-bit Integer, converted to float by dividing by 10^X|
|`sfloat32_X`|sint32|Signed 32-bit Integer, converted to float by dividing by 10^X|
|`stringX`|array|String (null terminated?) of max length X|
|`ufloat8_X`|sfloat32|Unsigned 8-bit Integer, converted to float by dividing by 10^X|
|`ufloat16_X`|sint16|Unsigned 16-bit Integer, converted to float by dividing by 10^X|
|`ufloat32_X`|sint32|Unsigned 32-bit Integer, converted to float by dividing by 10^X|
|`uint8`|uint8|Unsigned 8-bit Integer|
|`uint16`|uint16|Unsigned 16-bit Integer|
|`uint32`|uint32|Unsigned 32-bit Integer|
|`uint64`|uint64|Unsigned 64-bit Integer|

The mappings starting with '_' are for internal use by the interface generator. Anything else is considered a member and baked into the generated enum.