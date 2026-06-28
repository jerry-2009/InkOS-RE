# Fonts

Chinese text uses an external GB2312 HZK16 bitmap font.

Put the font file at one of these paths on the device:

```text
/fonts/HZK16
/sd/fonts/HZK16
```

The full HZK16 file is about 267 KB. InkOS reads only 32 bytes per Chinese
character while rendering, so RAM usage stays small.
