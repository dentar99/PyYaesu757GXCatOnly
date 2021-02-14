
NO WARRANTY
NO WARRANTY
NO WARRANTY
NO WARRANTY
NO WARRANTY

USE AT YOUR OWN RISK

        *******  NO SUPPORT OFFERED  *******

![PyYaesu757GXCatOnly](https://user-images.githubusercontent.com/76819904/107883968-2f396980-6ec0-11eb-998e-cba89e6d7e38.png)

Yaesu FT757-GX-1 program by N4LSJ

This program works for the FT-757GX -MARK 1- only.  The MK2 programming
is not quite the same, so this program is not considered compatible
with the FT-757GX 2.   This program is for experimental use and is
not professional programming.

SEE OCTOBER 1985 QST ARTICLE PAGE 38 TITLED, "A CAT Control System"

On page 39, a schematic is there for a circuit that uses a TIL-111
optoisolator.  You want the TIL-111 optoisolator circuit.  It's the
cleanest thing I've tried yet.  Other solutions can carry too much
noise for the overly sensitive TTL level serial interface.

The optoisolator circuit is driven by TTL level, not actual RS-232,
so you'll want to use TTL level serial, such as from an RS-232 to
TTL converter.  Don't wire the RS-232 straight to the circuit.

The FT757-GX speaks at one speed: 4800 baud.  Use stty or some such
to set your port speed before starting the program.

The connector on the back of the YAESU FT-757GX is called a
3-pin JST-XH with 2.54mm pitch

The first time you run this program, it will ask you for 
a Frequency, and a serial port.

If you get something wrong, you can edit or delete your .yaesuft757gxcat.conf
file and it will build new next time you run the program


DATA BYTE:
| START BIT | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | STOP BIT | STOP BIT |

5 BYTE BLOCK COMMAND
| PARM 4 (LSD) | PARM 3 | PARM 2 | PARM 1 | INSTRUCTION (MSD) |


