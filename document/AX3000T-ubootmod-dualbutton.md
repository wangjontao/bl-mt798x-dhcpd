# Xiaomi AX3000T U-Bootmod Dual-Key Build

This build targets the MT7981 Xiaomi AX3000T with SPI-NAND and the
ImmortalWrt/OpenWrt `ubootmod` layout:

```text
bl2 1 MiB | Nvram | Bdata | factory | fip 2 MiB | crash | crash_log | ubi 112 MiB | KF
```

The generated firmware includes:

- `*-fit.bin`: BL31 + U-Boot FIP for the `fip` MTD partition.
- `*.img`: matching BL2 preloader for the `bl2` MTD partition.

Flash both files. A FIP alone is not guaranteed to boot when the installed
preloader uses a different DRAM/NAND or UBI layout.

## Recovery keys

The default environment contains:

```text
glbtn_key=reset,mesh
```

At power-on, hold either the `reset` button or the `mesh` button for four
seconds to enter the Web failsafe UI. Holding both buttons also works.

The GPIO mapping matches the AX3000T DTS:

- `reset`: GPIO 1, active low
- `mesh`: GPIO 0, active low

The failsafe network address defaults to `192.168.1.1`.

## Before flashing

1. Enter the existing Web failsafe UI.
2. Back up all MTD partitions and export the U-Boot environment.
3. Confirm whether the router uses the standard PHY or the AN8855 switch.
4. Flash the matching BL2 image to `bl2`.
5. Flash the matching FIT FIP to `fip`.
6. Erase the `ubi` partition only after the BL2 and FIP writes succeed.
7. Boot the matching `xiaomi_mi-router-ax3000t-ubootmod` recovery or
   sysupgrade ITB.

Do not mix the standard and AN8855 images. Do not use these files with the
stock Xiaomi U-Boot layout or with an NMBM/MTK-U-Boot layout.
